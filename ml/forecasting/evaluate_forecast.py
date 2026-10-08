"""Evaluasi forecasting dengan time-series CV (expanding window, 3 fold x 14 hari) vs baseline naive lag-7."""
import os, sys
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

sys.path.insert(0, os.environ.get("BACKEND_PATH", "/app"))
from app.core.database import SessionLocal
from app.services.ml_service import FEATURES, _frame, daily_series

with SessionLocal() as db:
    s = daily_series(db)["total"]
df = _frame(s)
H, scores = 14, []
for k in (3, 2, 1):
    train, test = df.iloc[:-H * k], df.iloc[-H * k:-H * k + H]
    m = GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42).fit(train[FEATURES], train["y"])
    p, y = m.predict(test[FEATURES]), test["y"].values
    mae, rmse, mape = np.mean(abs(y - p)), np.sqrt(np.mean((y - p) ** 2)), np.mean(abs(y - p) / np.maximum(y, 1)) * 100
    base = np.mean(abs(y - test["lag7"].values))
    scores.append((mae, rmse, mape, base))
    print(f"fold(-{k * H}d)  MAE={mae:,.0f}  RMSE={rmse:,.0f}  MAPE={mape:.1f}%  baseline MAE={base:,.0f}")
print("rata-rata MAE=%.0f  MAPE=%.1f%%  baseline MAE=%.0f" % (np.mean([x[0] for x in scores]), np.mean([x[2] for x in scores]), np.mean([x[3] for x in scores])))
