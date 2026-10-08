"""Text-to-SQL: LLM -> SQL Generator -> SQL Validator -> Permission Checker -> Read-only DB -> Result."""
import re
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text

from app.constants import BRANCHES, CATEGORIES, PRODUCTS
from app.core.config import settings
from app.core.database import ro_engine
from app.services.llm_service import llm
from app.tools.sql_guard import SQLValidationError, validate_sql
from app.utils.dates import parse_period

SCHEMA_DESC = """PostgreSQL table `sales` (satu baris = satu transaksi penjualan):
  id INT, sale_date DATE, product_name TEXT, category TEXT, branch TEXT,
  quantity INT, unit_price NUMERIC, total_amount NUMERIC (Rupiah), customer_id INT
category: Elektronik | Furniture | Perlengkapan Kantor | Makanan & Minuman
branch: Jakarta | Bandung | Surabaya | Medan | Makassar
Data tersedia Januari-September 2026."""

SQL_SYSTEM = f"""Kamu adalah generator SQL PostgreSQL. Skema:
{SCHEMA_DESC}
Aturan: hanya satu query SELECT; hanya tabel sales; jangan memakai komentar; gunakan EXTRACT(MONTH/YEAR FROM sale_date)
untuk filter periode; beri alias kolom yang jelas; batasi hasil dengan LIMIT. Balas HANYA dengan SQL, tanpa penjelasan."""


def jsonable(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


def rule_based_sql(question: str) -> str:
    """Fallback tanpa LLM: pola pertanyaan penjualan yang umum."""
    q = question.lower()
    year, month = parse_period(question)
    conds = []
    if year:
        conds.append(f"EXTRACT(YEAR FROM sale_date) = {year}")
    if month:
        conds.append(f"EXTRACT(MONTH FROM sale_date) = {month}")
        if not year:
            conds.append("EXTRACT(YEAR FROM sale_date) = 2026")
    for b in BRANCHES:
        if b.lower() in q:
            conds.append(f"branch = '{b}'")
    for c in CATEGORIES:
        if c.lower() in q:
            conds.append(f"category = '{c}'")
    for p in PRODUCTS:
        if p[0].lower() in q:
            conds.append(f"product_name = '{p[0]}'")
    where = f"WHERE {' AND '.join(conds)}" if conds else ""
    if re.search(r"per\s+cabang|tiap\s+cabang|by\s+branch|cabang terbaik|cabang mana", q):
        return f"SELECT branch, SUM(total_amount) AS total_penjualan FROM sales {where} GROUP BY branch ORDER BY total_penjualan DESC"
    if re.search(r"per\s+kategori|tiap\s+kategori|by\s+category|kategori", q):
        return f"SELECT category, SUM(total_amount) AS total_penjualan FROM sales {where} GROUP BY category ORDER BY total_penjualan DESC"
    if re.search(r"produk.*(terlaris|teratas|top|terbaik)|(terlaris|top|terbaik).*produk|per\s+produk", q):
        return f"SELECT product_name, SUM(quantity) AS unit_terjual, SUM(total_amount) AS total_penjualan FROM sales {where} GROUP BY product_name ORDER BY total_penjualan DESC LIMIT 5"
    if re.search(r"per\s+bulan|bulanan|tiap\s+bulan|tren", q):
        return f"SELECT TO_CHAR(sale_date, 'YYYY-MM') AS bulan, SUM(total_amount) AS total_penjualan FROM sales {where} GROUP BY 1 ORDER BY 1"
    if re.search(r"jumlah transaksi|banyak transaksi|berapa transaksi", q):
        return f"SELECT COUNT(*) AS jumlah_transaksi FROM sales {where}"
    if re.search(r"pelanggan|customer", q):
        return f"SELECT COUNT(DISTINCT customer_id) AS jumlah_pelanggan FROM sales {where}"
    return f"SELECT SUM(total_amount) AS total_penjualan, COUNT(*) AS jumlah_transaksi FROM sales {where}"


def generate_sql(question: str, user_id=None) -> str:
    if llm.is_mock:
        return rule_based_sql(question)
    r = llm.chat([{"role": "system", "content": SQL_SYSTEM}, {"role": "user", "content": question}],
                 temperature=0, user_id=user_id, purpose="text_to_sql")
    return re.sub(r"^```(?:sql)?|```$", "", r["content"].strip(), flags=re.M).strip()


def run_select(sql: str) -> dict:
    safe = validate_sql(sql, settings.sql_max_rows)
    with ro_engine.connect() as conn:
        conn.execute(text("SET TRANSACTION READ ONLY"))
        conn.execute(text(f"SET LOCAL statement_timeout = {int(settings.sql_timeout_ms)}"))
        res = conn.execute(text(safe.replace(":", r"\:")))
        cols = list(res.keys())
        rows = [[jsonable(v) for v in r] for r in res.fetchmany(settings.sql_max_rows)]
        conn.rollback()
    return {"sql": safe, "columns": cols, "rows": rows, "row_count": len(rows)}


def query_database(ctx, question: str):
    sql = generate_sql(question, getattr(ctx.user, "id", None))
    try:
        return run_select(sql)
    except SQLValidationError as e:
        return {"error": f"Query ditolak oleh SQL validator: {e}", "sql": sql}
