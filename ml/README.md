# Machine Learning

Model dipakai langsung oleh backend (`backend/app/services/ml_service.py`). Skrip di sini untuk eksperimen/evaluasi offline.

| Komponen | Algoritma | Metrik |
|---|---|---|
| Sales forecasting | GradientBoostingRegressor + fitur kalender & lag (1/7/14) + rolling mean, forecast rekursif | MAE, RMSE, MAPE, dibanding baseline naive (lag-7) |
| Anomaly detection | Isolation Forest (harian: total/transaksi/avg-ticket; transaksi: log nominal, qty, harga) | jumlah anomali, z-score |

Jalankan evaluasi (dari dalam container backend):
```bash
docker compose exec backend python /ml/forecasting/evaluate_forecast.py
docker compose exec backend python /ml/anomaly_detection/run_anomaly.py
```
Atau dari host dengan `pip install -r backend/requirements.txt` dan `DATABASE_URL` mengarah ke Postgres (`localhost:5432`).
Ide pengembangan: XGBoost/LightGBM/Prophet, tuning dengan time-series cross-validation, label anomali nyata untuk Precision/Recall/F1.
