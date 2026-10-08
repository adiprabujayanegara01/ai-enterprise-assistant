import re

# Pola instruksi berbahaya yang sering disisipkan pada dokumen (prompt injection).
_PATTERNS = [
    r"ignore\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
    r"disregard\s+.{0,40}instructions?",
    r"abaikan\s+(semua\s+|seluruh\s+)?(instruksi|perintah|aturan)(\s+sebelumnya)?",
    r"lupakan\s+(semua\s+)?(instruksi|perintah|aturan)",
    r"you\s+are\s+now\b",
    r"kamu\s+sekarang\s+adalah",
    r"(reveal|show|print|tampilkan|bocorkan)\s+.{0,30}(system\s+prompt|api\s*key|password|secret|rahasia)",
    r"</?\s*(system|assistant|context|tool)\s*>",
    r"\[/?INST\]|<\|im_(start|end)\|>",
]
_RX = re.compile("|".join(_PATTERNS), re.I)


def sanitize_context(text: str) -> str:
    """Perlakukan isi dokumen sebagai DATA: netralkan teks yang menyerupai instruksi."""
    return _RX.sub("[INSTRUKSI-DIHAPUS]", text or "")


def looks_injected(text: str) -> bool:
    return bool(_RX.search(text or ""))
