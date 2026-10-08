import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.core.security import get_current_user
from app.models import Conversation, Message, User
from app.schemas import ChatIn, ChatOut
from app.services import rag_service
from app.services.agent_service import agent_service
from app.services.llm_service import llm

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _conv(db: Session, user: User, data: ChatIn) -> Conversation:
    if data.conversation_id:
        c = db.get(Conversation, data.conversation_id)
        if not c or c.user_id != user.id:
            raise HTTPException(404, "Percakapan tidak ditemukan")
        return c
    c = Conversation(user_id=user.id, title=data.message[:60])
    db.add(c); db.commit()
    return c


def _history(db: Session, conv_id: int) -> List[dict]:
    msgs = db.scalars(select(Message).where(Message.conversation_id == conv_id).order_by(Message.id)).all()
    return [{"role": m.role, "content": m.content} for m in msgs]


@router.post("", response_model=ChatOut)
def chat(data: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = _conv(db, user, data)
    hist = _history(db, conv.id)
    db.add(Message(conversation_id=conv.id, role="user", content=data.message))
    conv.updated_at = func.now(); db.commit()
    if data.mode == "agent":
        r = agent_service.run(db, user, data.message, hist)
        answer, sources, tools = r["answer"], [], r["tools_used"]
    else:
        r = rag_service.answer(db, user, data.message, hist)
        answer, sources, tools = r["answer"], r["sources"], []
    db.add(Message(conversation_id=conv.id, role="assistant", content=answer, sources=sources, tools_used=tools))
    db.commit()
    return ChatOut(answer=answer, sources=sources, tools_used=tools, conversation_id=conv.id)


@router.post("/stream")
def chat_stream(data: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Server-Sent Events: event meta -> token* -> sources -> done."""
    conv = _conv(db, user, data)
    hist = _history(db, conv.id)
    db.add(Message(conversation_id=conv.id, role="user", content=data.message))
    conv.updated_at = func.now(); db.commit()
    conv_id, user_id, role_user = conv.id, user.id, user
    msgs, sources = rag_service.prepare(db, user, data.message, hist)

    def sse(event: str, payload) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def gen():
        yield sse("meta", {"conversation_id": conv_id})
        full = []
        try:
            for tok in llm.stream(msgs, user_id=user_id):
                full.append(tok)
                yield sse("token", tok)
        except Exception as e:  # noqa
            err = f"\n\n[Error LLM: {e}]"
            full.append(err)
            yield sse("token", err)
        yield sse("sources", sources)
        with SessionLocal() as s:  # session sendiri: dependency session bisa sudah ditutup saat streaming
            s.add(Message(conversation_id=conv_id, role="assistant", content="".join(full), sources=sources))
            s.commit()
        yield sse("done", {})

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc())).all()
    return [{"id": c.id, "title": c.title, "updated_at": c.updated_at} for c in rows]


@router.get("/{conversation_id}")
def get_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.get(Conversation, conversation_id)
    if not c or c.user_id != user.id:
        raise HTTPException(404, "Percakapan tidak ditemukan")
    return {"id": c.id, "title": c.title, "messages": [
        {"id": m.id, "role": m.role, "content": m.content, "sources": m.sources or [], "tools_used": m.tools_used or []}
        for m in c.messages]}


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.get(Conversation, conversation_id)
    if not c or c.user_id != user.id:
        raise HTTPException(404, "Percakapan tidak ditemukan")
    db.delete(c); db.commit()
