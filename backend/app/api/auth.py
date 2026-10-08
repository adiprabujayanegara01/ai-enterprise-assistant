from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.database import get_db
from app.core.security import create_token, get_current_user, hash_password, require_role, verify_password
from app.models import User
from app.schemas import LoginIn, RegisterIn, RoleIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _ip(req: Request) -> str:
    return req.headers.get("x-forwarded-for", req.client.host if req.client else "").split(",")[0].strip()


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, request: Request, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(409, "Email sudah terdaftar")
    user = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password), role="EMPLOYEE")
    db.add(user); db.commit()
    audit(db, user.id, "REGISTER", user.email, _ip(request))
    return TokenOut(access_token=create_token(user), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        audit(db, user.id if user else None, "LOGIN_FAILED", data.email, _ip(request))
        raise HTTPException(401, "Email atau password salah")
    audit(db, user.id, "LOGIN", user.email, _ip(request))
    return TokenOut(access_token=create_token(user), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=List[UserOut])
def users(_: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/users/{user_id}/role", response_model=UserOut)
def set_role(user_id: int, data: RoleIn, request: Request, admin: User = Depends(require_role("ADMIN")),
             db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User tidak ditemukan")
    target.role = data.role
    db.commit()
    audit(db, admin.id, "ROLE_CHANGE", f"user={user_id} role={data.role}", _ip(request))
    return target
