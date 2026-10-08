"""SQL validator: hanya SELECT/CTE tunggal, tabel di allowlist, tanpa komentar/fungsi berbahaya, LIMIT wajib."""
import re

ALLOWED_TABLES = {"sales"}


class SQLValidationError(ValueError):
    pass


_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|merge|call|execute|vacuum|analyze|"
    r"reindex|listen|notify|lock|set|reset|do|into|pg_sleep|pg_read_file|pg_ls_dir|lo_import|lo_export|dblink|"
    r"current_setting|set_config)\b", re.I)
_LITERAL_OR_COMMENT = re.compile(r"('(?:[^']|'')*')|--[^\n]*|/\*.*?\*/", re.S)


def validate_sql(sql: str, max_rows: int = 200) -> str:
    if not sql or not sql.strip():
        raise SQLValidationError("Query kosong")
    # buang komentar (komentar bisa menyembunyikan LIMIT/klausa), pertahankan literal
    no_comment = _LITERAL_OR_COMMENT.sub(lambda m: m.group(1) or " ", sql).strip().rstrip(";").strip()
    cleaned = re.sub(r"'(?:[^']|'')*'", "''", no_comment)  # literal dikosongkan untuk analisis
    if ";" in cleaned:
        raise SQLValidationError("Hanya satu statement yang diizinkan")
    if '"' in cleaned:
        raise SQLValidationError("Identifier dengan tanda kutip ganda tidak diizinkan")
    if not re.match(r"^(select|with)\b", cleaned, re.I):
        raise SQLValidationError("Hanya query SELECT yang diizinkan")
    bad = _FORBIDDEN.search(cleaned)
    if bad:
        raise SQLValidationError(f"Kata kunci tidak diizinkan: {bad.group(0).upper()}")
    if re.search(r"\b(pg_\w+|information_schema|pg_catalog)\b", cleaned, re.I):
        raise SQLValidationError("Akses ke katalog sistem tidak diizinkan")

    norm = re.sub(r"\b(extract|substring|trim|overlay|position)\s*\(([^()]*?)\bfrom\b", r"\1(\2,", cleaned, flags=re.I)
    ctes = {c.lower() for c in re.findall(r"(?:\bwith|,)\s*([a-z_]\w*)\s+as\s*\(", norm, re.I)}
    if re.search(r"\bfrom\s+[a-z_][\w\.]*(?:\s+(?:as\s+)?[a-z_]\w*)?\s*,\s*[a-z_(]", norm, re.I):
        raise SQLValidationError("Gunakan JOIN eksplisit, bukan daftar tabel dengan koma")
    for t in re.findall(r"\b(?:from|join)\s+([a-z_][\w\.]*)", norm, re.I):
        name = t.lower().removeprefix("public.")
        if name not in ALLOWED_TABLES and name not in ctes:
            raise SQLValidationError(f"Tabel '{t}' tidak diizinkan. Tabel tersedia: {', '.join(sorted(ALLOWED_TABLES))}")
    if not re.search(r"\blimit\s+\d+", norm, re.I):
        no_comment += f" LIMIT {max_rows}"
    return no_comment
