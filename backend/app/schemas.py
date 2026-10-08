from datetime import datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RoleIn(BaseModel):
    role: Literal["ADMIN", "MANAGER", "EMPLOYEE"]


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: Optional[int] = None
    mode: Literal["rag", "agent"] = "rag"


class ChatOut(BaseModel):
    answer: str
    sources: List[dict] = []
    tools_used: List[str] = []
    conversation_id: int


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    file_type: str
    status: str
    error: Optional[str] = None
    access_level: str
    used_ocr: bool
    page_count: int
    chunk_count: int
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None


class AgentRunIn(BaseModel):
    query: str = Field(min_length=1, max_length=4000)


class AgentRunOut(BaseModel):
    answer: str
    tools_used: List[str]
    execution_time: float
    run_id: Optional[int] = None
    steps: List[dict[str, Any]] = []
