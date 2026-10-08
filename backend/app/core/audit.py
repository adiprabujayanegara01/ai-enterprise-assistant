from typing import Optional
from sqlalchemy.orm import Session
from app.models import AuditLog


def audit(db: Session, user_id: Optional[int], action: str, detail: str = "", ip: str = "") -> None:
    db.add(AuditLog(user_id=user_id, action=action, detail=detail[:2000], ip=ip))
    db.commit()
