import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, text

from app import models  # noqa: F401  (registrasi tabel)
from app.api import agent, analytics, auth, chat, documents
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.ratelimit import allow
from app.core.security import hash_password
from app.services.llm_service import llm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app")


def init_db():
    for attempt in range(30):  # tunggu Postgres siap
        try:
            with engine.begin() as c:
                c.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            break
        except Exception as e:  # noqa
            log.warning("Menunggu database (%s): %s", attempt + 1, str(e)[:80])
            time.sleep(2)
    Base.metadata.create_all(engine)
    for ddl in ("CREATE INDEX IF NOT EXISTS ix_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops)",
                "CREATE INDEX IF NOT EXISTS ix_chunks_fts ON document_chunks USING gin (to_tsvector('simple', content))"):
        try:
            with engine.begin() as c:
                c.execute(text(ddl))
        except Exception as e:  # noqa
            log.warning("Index dilewati: %s", str(e)[:100])


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        if not db.scalar(select(models.User.id).limit(1)):
            db.add(models.User(name=settings.admin_name, email=settings.admin_email.lower(),
                               password_hash=hash_password(settings.admin_password), role="ADMIN"))
            db.commit()
        has_sales = db.scalar(select(func.count(models.Sale.id))) > 0
    if settings.auto_seed and not has_sales:
        from app.seed import seed_all
        seed_all()
    log.info("AI Enterprise Assistant siap (LLM provider: %s)", settings.llm_provider)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan,
              description="Enterprise AI: RAG, OCR, AI Agent, Text-to-SQL, ML & BI")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = "REQ-" + uuid.uuid4().hex[:8].upper()
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0].strip()
    if request.url.path.startswith("/api") and not allow(ip):
        return JSONResponse({"detail": "Terlalu banyak permintaan. Coba lagi sebentar."}, status_code=429)
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    response.headers["X-Request-ID"] = rid
    response.headers["X-Content-Type-Options"] = "nosniff"
    log.info("%s %s %s -> %s (%.0f ms) ip=%s", rid, request.method, request.url.path, response.status_code, ms, ip)
    return response


for r in (auth.router, chat.router, documents.router, agent.router, analytics.router):
    app.include_router(r)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "llm_provider": settings.llm_provider, "mock_mode": llm.is_mock}
