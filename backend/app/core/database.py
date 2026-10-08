from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
# Engine terpisah (idealnya user DB read-only) khusus untuk SQL Agent
ro_engine = create_engine(settings.readonly_database_url or settings.database_url, pool_pre_ping=True, pool_size=3)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
