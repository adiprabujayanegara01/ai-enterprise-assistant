from datetime import date, datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="EMPLOYEE")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(20))
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="UPLOADED")  # UPLOADED|PROCESSING|READY|FAILED
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_level: Mapped[str] = mapped_column(String(20), default="EMPLOYEE")
    used_ocr: Mapped[bool] = mapped_column(default=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    chunks = relationship("DocumentChunk", cascade="all, delete-orphan", passive_deletes=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    section: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    embedding = mapped_column(Vector(settings.embedding_dim))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="Percakapan baru")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    messages = relationship("Message", cascade="all, delete-orphan", passive_deletes=True, order_by="Message.id")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tools_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    query: Mapped[str] = mapped_column(Text)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools_used: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="RUNNING")
    execution_time: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    tool_calls = relationship("ToolCall", cascade="all, delete-orphan", passive_deletes=True, order_by="ToolCall.id")


class ToolCall(Base):
    __tablename__ = "tool_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True)
    tool_name: Mapped[str] = mapped_column(String(80))
    tool_input: Mapped[dict] = mapped_column(JSON, default=dict)
    tool_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OK")
    duration: Mapped[float] = mapped_column(Float, default=0)


class AIUsage(Base):
    __tablename__ = "ai_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    model: Mapped[str] = mapped_column(String(80))
    purpose: Mapped[str] = mapped_column(String(40), default="chat")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency: Mapped[float] = mapped_column(Float, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_date: Mapped[date] = mapped_column(Date, index=True)
    product_name: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    branch: Mapped[str] = mapped_column(String(80), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 2))
    total_amount: Mapped[float] = mapped_column(Numeric(16, 2))
    customer_id: Mapped[int] = mapped_column(Integer, index=True)
