"""Komponen Machine Learning: Sales Forecasting (GradientBoosting + lag features) & Anomaly Detection (Isolation Forest)."""
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, IsolationForest
from sqlalchemy import text
from sqlalchemy.orm import Session

FEATURES = ["dow", "dom", "month", "lag1", "lag7", "lag14", "roll7"]


def daily_series(db: Session) -> pd.DataFrame:
    df = pd.read_sql(text("SELECT sale_date AS d, SUM(total_amount) AS total, COUNT(*) AS tx FROM sales GROUP BY 1 ORDER BY 1"),
                     db.connection())
    if df.empty:
        return df
    df["d"] = pd.to_datetime(df["d"])
    df = df.set_index("d").astype(float)
    return df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D"), fill_value=0.0)


def _row(hist: pd.Series, day: pd.Timestamp) -> dict:
    return {"dow": day.dayofweek, "dom": day.day, "month": day.month,
            "lag1": hist.iloc[-1], "lag7": hist.iloc[-7], "lag14": hist.iloc[-14], "roll7": hist.iloc[-7:].mean()}


def _frame(s: pd.Series) -> pd.DataFrame:
    rows = [{**_row(s.iloc[:i], s.index[i]), "y": s.iloc[i]} for i in range(14, len(s))]
    return pd.DataFrame(rows, index=s.index[14:])


def forecast_sales(db: Session, horizon_days: int = 30) -> dict:
    daily = daily_series(db)
    if len(daily) < 60:
        return {"error": "Data historis belum cukup (minimal 60 hari)"}
    s = daily["total"]
    df = _frame(s)
    holdout = 14
    train, test = df.iloc[:-holdout], df.iloc[-holdout:]
    mk = lambda: GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
    pred = mk().fit(train[FEATURES], train["y"]).predict(test[FEATURES])
    err = test["y"].values - pred
    mape = float(np.mean(np.abs(err) / np.maximum(test["y"].values, 1)) * 100)
    base = float(np.mean(np.abs(test["y"].values - test["lag7"].values)))  # baseline naive seasonal
    metrics = {"mae": round(float(np.mean(np.abs(err))), 0), "rmse": round(float(np.sqrt(np.mean(err ** 2))), 0),
               "mape": round(mape, 2), "baseline_mae_naive_lag7": round(base, 0), "holdout_days": holdout}
    model = mk().fit(df[FEATURES], df["y"])
    hist, out = s.copy(), []
    for _ in range(max(1, min(horizon_days, 90))):
        day = hist.index[-1] + pd.Timedelta(days=1)
        v = max(float(model.predict(pd.DataFrame([_row(hist, day)])[FEATURES])[0]), 0.0)
        hist.loc[day] = v
        out.append({"date": day.date().isoformat(), "value": round(v, 0)})
    tail = s.iloc[-60:]
    return {"history": [{"date": d.date().isoformat(), "value": round(float(v), 0)} for d, v in tail.items()],
            "forecast": out, "metrics": metrics, "total_forecast": round(sum(o["value"] for o in out), 0),
            "model": "GradientBoostingRegressor (lag & kalender features)"}


def detect_anomalies(db: Session, year: Optional[int] = None, month: Optional[int] = None) -> dict:
    daily = daily_series(db)
    if daily.empty:
        return {"daily": [], "transactions": [], "transaction_anomaly_count": 0}
    # --- level harian ---
    X = pd.DataFrame({"total": daily["total"], "tx": daily["tx"], "ticket": daily["total"] / daily["tx"].clip(lower=1)})
    Xs = (X - X.mean()) / X.std().replace(0, 1)
    flag = IsolationForest(contamination=0.03, random_state=42).fit_predict(Xs) == -1
    z = (daily["total"] - daily["total"].mean()) / (daily["total"].std() or 1)
    d_out = [{"date": d.date().isoformat(), "total": round(float(daily.loc[d, "total"]), 0), "transactions": int(daily.loc[d, "tx"]),
              "z_score": round(float(z[d]), 2), "reason": "Penjualan harian jauh di atas normal" if z[d] > 0 else "Penjualan harian jauh di bawah normal"}
             for d in daily.index[flag]]
    # --- level transaksi ---
    tx = pd.read_sql(text("SELECT id, sale_date, product_name, branch, quantity, unit_price, total_amount FROM sales"), db.connection())
    tx[["quantity", "unit_price", "total_amount"]] = tx[["quantity", "unit_price", "total_amount"]].astype(float)
    feats = np.column_stack([np.log1p(tx["total_amount"]), tx["quantity"], np.log1p(tx["unit_price"])])
    iso = IsolationForest(contamination=0.0025, random_state=42).fit(feats)
    tx["score"] = -iso.score_samples(feats)
    tx["anomaly"] = iso.predict(feats) == -1
    tx["sale_date"] = pd.to_datetime(tx["sale_date"])
    if year:
        tx = tx[tx["sale_date"].dt.year == year]
    if month:
        tx = tx[tx["sale_date"].dt.month == month]
    if year or month:
        d_out = [d for d in d_out if (not year or d["date"].startswith(str(year))) and (not month or int(d["date"][5:7]) == month)]
    a = tx[tx["anomaly"]].sort_values("score", ascending=False)
    top = [{"id": int(r.id), "date": r.sale_date.date().isoformat(), "product": r.product_name, "branch": r.branch,
            "quantity": int(r.quantity), "total_amount": float(r.total_amount), "score": round(float(r.score), 3)}
           for r in a.head(20).itertuples()]
    return {"daily": d_out, "transactions": top, "transaction_anomaly_count": int(len(a)),
            "method": "Isolation Forest (harian & transaksi)"}
