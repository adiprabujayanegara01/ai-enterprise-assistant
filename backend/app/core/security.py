from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.constants import ROLE_RANK
from app.core.config import settings
from app.core.database import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


def create_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": str(user.id), "role": user.role, "exp": exp},
                      settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token tidak valid atau kedaluwarsa")
    if not creds:
        raise err
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise err
    if not user:
        raise err
    return user


def has_role(user: User, min_role: str) -> bool:
    return ROLE_RANK.get(user.role, 0) >= ROLE_RANK[min_role]


def require_role(min_role: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        if not has_role(user, min_role):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Dibutuhkan peran minimal {min_role}")
        return user
    return dep
