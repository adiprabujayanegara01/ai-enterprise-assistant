"""Seed: user demo, data penjualan sintetis (Jan-Sep 2026, ada penurunan di September), dan dokumen contoh."""
import logging
import os
import shutil
import uuid
from datetime import date, timedelta

import numpy as np
from sqlalchemy import insert, select

from app.constants import BRANCHES, PRODUCTS
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Document, Sale, User
from app.services.document_service import ingest_document

log = logging.getLogger("seed")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
SAMPLE_DOCS = {  # file -> access level
    "SOP_Reimbursement_Finance.txt": "EMPLOYEE",
    "Kebijakan_Cuti_HR.txt": "EMPLOYEE",
    "Laporan_Operasional_Agustus_September_2026.txt": "MANAGER",
}
DEMO_USERS = [("Manager Demo", "manager@company.com", "Manager123!", "MANAGER"),
              ("Karyawan Demo", "employee@company.com", "Employee123!", "EMPLOYEE")]


def seed_users(db):
    for name, email, pw, role in DEMO_USERS:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(name=name, email=email, password_hash=hash_password(pw), role=role))
    db.commit()


def gen_sales(seed: int = 42):
    rng = np.random.default_rng(seed)
    names = [p[0] for p in PRODUCTS]
    base_w = np.array([p[3] for p in PRODUCTS])
    branch_w = np.array([0.30, 0.18, 0.22, 0.15, 0.15])
    rows, d = [], date(2026, 1, 1)
    while d <= date(2026, 9, 30):
        n = rng.normal(62, 6) * (1 + 0.012 * (d.month - 1)) * (1.18 if d.weekday() >= 5 else 1.0)
        if d.month == 9:
            n *= 1.03
        if date(2026, 9, 15) <= d <= date(2026, 9, 19):  # gangguan distribusi (banjir)
            n *= 0.7
        for _ in range(max(10, int(n))):
            w, bw = base_w.copy(), branch_w.copy()
            if d.month == 9:
                bw[BRANCHES.index("Surabaya")] *= 0.8       # cabang Surabaya turun
                for i, p in enumerate(PRODUCTS):
                    if p[1] == "Elektronik":
                        w[i] *= 0.93                          # pasokan elektronik terlambat
            i = rng.choice(len(PRODUCTS), p=w / w.sum())
            name, cat, price, _w = PRODUCTS[i]
            qty = int(rng.integers(1, 5)) if price < 3_000_000 else int(rng.integers(1, 3))
            unit = round(price * rng.uniform(0.95, 1.05), -2)
            rows.append({"sale_date": d, "product_name": name, "category": cat,
                         "branch": BRANCHES[rng.choice(5, p=bw / bw.sum())], "quantity": qty,
                         "unit_price": unit, "total_amount": unit * qty, "customer_id": int(rng.integers(1, 3000))})
        d += timedelta(days=1)
    cheap = [r for r in rows if float(r["unit_price"]) < 3_000_000]
    for _ in range(14):  # anomali transaksi (kuantitas tidak wajar)
        r = dict(cheap[int(rng.integers(0, len(cheap)))])
        r["quantity"] = int(rng.integers(35, 70)); r["total_amount"] = r["unit_price"] * r["quantity"]
        rows.append(r)
    return rows


def seed_sales(db):
    rows = gen_sales()
    for i in range(0, len(rows), 2000):
        db.execute(insert(Sale), rows[i:i + 2000])
    db.commit()
    log.info("Seed: %d transaksi penjualan", len(rows))


def seed_documents(db):
    admin = db.scalar(select(User).where(User.role == "ADMIN"))
    os.makedirs(settings.upload_dir, exist_ok=True)
    for fname, level in SAMPLE_DOCS.items():
        src = os.path.join(SAMPLE_DIR, fname)
        if not os.path.isfile(src) or db.scalar(select(Document).where(Document.filename == fname)):
            continue
        dest = os.path.join(settings.upload_dir, f"{uuid.uuid4().hex}.txt")
        shutil.copy(src, dest)
        doc = Document(filename=fname, file_type="txt", file_path=dest, status="UPLOADED", access_level=level,
                       uploaded_by=admin.id if admin else None)
        db.add(doc); db.commit()
        ingest_document(doc.id)


def seed_all():
    with SessionLocal() as db:
        seed_users(db)
        if not db.scalar(select(Sale.id).limit(1)):
            seed_sales(db)
        seed_documents(db)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_all()
