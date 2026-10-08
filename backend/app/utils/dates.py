import re
from app.constants import MONTH_NAMES

_ALIASES = {
    "januari": 1, "january": 1, "februari": 2, "february": 2, "maret": 3, "march": 3,
    "april": 4, "mei": 5, "may": 5, "juni": 6, "june": 6, "juli": 7, "july": 7,
    "agustus": 8, "august": 8, "september": 9, "oktober": 10, "october": 10,
    "november": 11, "desember": 12, "december": 12,
}


def parse_period(text: str):
    """Ambil (tahun, bulan) dari teks bebas. Nilai yang tidak ditemukan -> None."""
    t = text.lower()
    month = None
    for name, num in _ALIASES.items():
        if re.search(rf"\b{name}\b", t):
            month = num
            break
    ym = re.search(r"\b(20\d\d)\b", t)
    return (int(ym.group(1)) if ym else None), month


def prev_month(year: int, month: int):
    return (year - 1, 12) if month == 1 else (year, month - 1)


def label(year: int, month: int) -> str:
    return f"{MONTH_NAMES[month]} {year}"


def fmt_rp(v: float) -> str:
    v = float(v or 0)
    if abs(v) >= 1e9:
        return f"Rp{v / 1e9:.2f} M".replace(".", ",")
    if abs(v) >= 1e6:
        return f"Rp{v / 1e6:.1f} jt".replace(".", ",")
    return f"Rp{v:,.0f}".replace(",", ".")


def growth_pct(cur: float, prev: float):
    cur, prev = float(cur or 0), float(prev or 0)
    if prev == 0:
        return None
    return round((cur - prev) / prev * 100, 2)
