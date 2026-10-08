from app.services import ml_service


def forecast_sales(ctx, horizon_days: int = 30):
    r = ml_service.forecast_sales(ctx.db, int(horizon_days))
    if "error" in r:
        return r
    r["history"] = r["history"][-7:]  # ringkas untuk konteks LLM
    return r


def detect_anomalies(ctx, year: int = None, month: int = None):
    r = ml_service.detect_anomalies(ctx.db, year, month)
    r["transactions"] = r["transactions"][:5]
    return r
