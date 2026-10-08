from app.services.rag_service import retrieve
from app.utils.sanitize import sanitize_context


def search_documents(ctx, query: str, top_k: int = 4):
    hits = retrieve(ctx.db, ctx.user, query, k=top_k)
    return {"results": [{"document": h["filename"], "page": h["page"], "section": h["section"],
                         "text": sanitize_context(h["content"])[:600]} for h in hits]}
