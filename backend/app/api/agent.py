import os
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, has_role
from app.models import AgentRun, User
from app.schemas import AgentRunIn, AgentRunOut
from app.services.agent_service import TOOLS, agent_service

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunOut)
def run(data: AgentRunIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    audit(db, user.id, "AGENT_RUN", data.query[:300])
    return agent_service.run(db, user, data.query)


@router.get("/tools")
def tools(user: User = Depends(get_current_user)):
    return [{"name": t["name"], "description": t["schema"]["description"], "min_role": t["min_role"],
             "allowed": has_role(user, t["min_role"])} for t in TOOLS.values()]


def _visible(user: User):
    return select(AgentRun) if has_role(user, "ADMIN") else select(AgentRun).where(AgentRun.user_id == user.id)


@router.get("/runs")
def runs(limit: int = 50, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(_visible(user).order_by(AgentRun.id.desc()).limit(min(limit, 200))).all()
    return [{"id": r.id, "user_id": r.user_id, "query": r.query, "tools_used": r.tools_used, "status": r.status,
             "execution_time": r.execution_time, "created_at": r.created_at} for r in rows]


@router.get("/runs/{run_id}")
def run_detail(run_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.scalars(_visible(user).where(AgentRun.id == run_id)).first()
    if not r:
        raise HTTPException(404, "Run tidak ditemukan")
    return {"id": r.id, "query": r.query, "answer": r.answer, "status": r.status, "execution_time": r.execution_time,
            "tools_used": r.tools_used, "created_at": r.created_at,
            "tool_calls": [{"tool_name": t.tool_name, "tool_input": t.tool_input, "tool_output": (t.tool_output or "")[:3000],
                            "status": t.status, "duration": t.duration} for t in r.tool_calls]}


@router.get("/reports/{filename}")
def report(filename: str, user: User = Depends(get_current_user)):
    if not re.fullmatch(r"[a-z0-9\-]+\.md", filename):  # cegah path traversal
        raise HTTPException(400, "Nama file tidak valid")
    path = os.path.join(settings.reports_dir, filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "Laporan tidak ditemukan")
    return FileResponse(path, media_type="text/markdown", filename=filename)
