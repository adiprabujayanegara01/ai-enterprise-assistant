"""Jalankan deteksi anomali & cetak ringkasan."""
import os, sys
sys.path.insert(0, os.environ.get("BACKEND_PATH", "/app"))
from app.core.database import SessionLocal
from app.services.ml_service import detect_anomalies

with SessionLocal() as db:
    r = detect_anomalies(db)
print("Transaksi anomali:", r["transaction_anomaly_count"], "| Hari anomali:", len(r["daily"]))
for t in r["transactions"][:10]:
    print(t)
for d in r["daily"]:
    print(d)
