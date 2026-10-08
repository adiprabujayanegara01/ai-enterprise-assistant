from datetime import date
from typing import Optional, Tuple

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models import Sale
from app.utils.dates import growth_pct, label, prev_month


def latest_period(db: Session) -> Tuple[int, int]:
    d = db.scalar(select(func.max(Sale.sale_date))) or date.today()
    return d.year, d.month


def resolve(db: Session, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
    ly, lm = latest_period(db)
    return (year or ly), (month or (lm if not year or year == ly else 12))


def _period(y, m):
    return (extract("year", Sale.sale_date) == y) & (extract("month", Sale.sale_date) == m)


def month_totals(db: Session, y: int, m: int) -> dict:
    r = db.execute(select(func.coalesce(func.sum(Sale.total_amount), 0), func.count(Sale.id),
                          func.count(func.distinct(Sale.customer_id))).where(_period(y, m))).one()
    return {"total": float(r[0]), "transactions": int(r[1]), "customers": int(r[2]), "label": label(y, m)}


def by_dim(db: Session, y: int, m: int, dim: str) -> dict:
    col = {"category": Sale.category, "branch": Sale.branch, "product": Sale.product_name}[dim]
    rows = db.execute(select(col, func.sum(Sale.total_amount)).where(_period(y, m)).group_by(col)).all()
    return {k: float(v) for k, v in rows}


def compare_dim(db: Session, y: int, m: int, dim: str) -> list:
    py, pm = prev_month(y, m)
    cur, prev = by_dim(db, y, m, dim), by_dim(db, py, pm, dim)
    out = [{"name": k, "current": cur.get(k, 0), "previous": prev.get(k, 0), "growth_pct": growth_pct(cur.get(k, 0), prev.get(k, 0))}
           for k in sorted(set(cur) | set(prev))]
    return sorted(out, key=lambda x: (x["growth_pct"] is None, x["growth_pct"] or 0))


def sales_report(db: Session, year: Optional[int] = None, month: Optional[int] = None) -> dict:
    y, m = resolve(db, year, month)
    py, pm = prev_month(y, m)
    cur, prev = month_totals(db, y, m), month_totals(db, py, pm)
    return {"period": f"{y}-{m:02d}", "label": cur["label"], "year": y, "month": m, "current": cur, "previous": prev,
            "growth_pct": growth_pct(cur["total"], prev["total"]),
            "transactions_growth_pct": growth_pct(cur["transactions"], prev["transactions"]),
            "customers_growth_pct": growth_pct(cur["customers"], prev["customers"]),
            "by_category": compare_dim(db, y, m, "category"), "by_branch": compare_dim(db, y, m, "branch"),
            "top_products": sorted(compare_dim(db, y, m, "product"), key=lambda x: -x["current"])[:5]}


def monthly_series(db: Session) -> list:
    y, m = extract("year", Sale.sale_date), extract("month", Sale.sale_date)
    rows = db.execute(select(y, m, func.sum(Sale.total_amount), func.count(Sale.id)).group_by(y, m).order_by(y, m)).all()
    return [{"month": f"{int(a)}-{int(b):02d}", "total": float(t), "transactions": int(c)} for a, b, t, c in rows]
