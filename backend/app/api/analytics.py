from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models import AIUsage, AuditLog, User
from app.services import analytics_service as an
from app.services import ml_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
Manager = Depends(require_role("MANAGER"))


@router.get("/summary")
def summary(year: Optional[int] = None, month: Optional[int] = None, _: User = Manager, db: Session = Depends(get_db)):
    rep = an.sales_report(db, year, month)
    rep["anomaly_count"] = ml_service.detect_anomalies(db, rep["year"], rep["month"])["transaction_anomaly_count"]
    return rep


@router.get("/monthly")
def monthly(_: User = Manager, db: Session = Depends(get_db)):
    return an.monthly_series(db)


@router.get("/forecast")
def forecast(horizon: int = Query(30, ge=7, le=90), _: User = Manager, db: Session = Depends(get_db)):
    return ml_service.forecast_sales(db, horizon)


@router.get("/anomalies")
def anomalies(year: Optional[int] = None, month: Optional[int] = None, _: User = Manager, db: Session = Depends(get_db)):
    return ml_service.detect_anomalies(db, year, month)


@router.get("/usage")
def usage(_: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    tot = db.execute(select(func.count(AIUsage.id), func.coalesce(func.sum(AIUsage.total_tokens), 0),
                            func.coalesce(func.sum(AIUsage.estimated_cost), 0), func.coalesce(func.avg(AIUsage.latency), 0))).one()
    recent = db.scalars(select(AIUsage).order_by(AIUsage.id.desc()).limit(30)).all()
    return {"requests": tot[0], "total_tokens": int(tot[1]), "estimated_cost_usd": round(float(tot[2]), 4),
            "avg_latency_s": round(float(tot[3]), 2),
            "recent": [{"id": u.id, "user_id": u.user_id, "model": u.model, "purpose": u.purpose, "tokens": u.total_tokens,
                        "latency": u.latency, "created_at": u.created_at} for u in recent]}


@router.get("/audit")
def audit_log(limit: int = 100, _: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(min(limit, 500))).all()
    return [{"id": a.id, "user_id": a.user_id, "action": a.action, "detail": a.detail, "ip": a.ip, "created_at": a.created_at} for a in rows]
