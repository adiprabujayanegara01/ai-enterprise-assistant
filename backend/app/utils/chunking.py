import re
from typing import List, Tuple

_HEADING = re.compile(r"^(\d+[\.\)]\s+.{3,80}|[A-Z][A-Z0-9 &/\-]{4,80}|#{1,4}\s+.+)$")


def _split_text(text: str, size: int, overlap: int) -> List[str]:
    """Recursive splitter: paragraf -> kalimat -> karakter, dengan overlap."""
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) <= size:
        return [text] if text else []
    parts, buf = [], ""
    units = re.split(r"(?<=\n\n)|(?<=[\.\?\!])\s+", text)
    for u in units:
        if not u:
            continue
        while len(u) > size:  # satuan terlalu panjang -> potong paksa
            if buf:
                parts.append(buf); buf = ""
            parts.append(u[:size]); u = u[size - overlap:]
        if len(buf) + len(u) + 1 <= size:
            buf = f"{buf} {u}".strip() if buf else u
        else:
            parts.append(buf)
            tail = buf[-overlap:] if overlap else ""
            buf = f"{tail} {u}".strip()
    if buf:
        parts.append(buf)
    return [p.strip() for p in parts if p.strip()]


def chunk_pages(pages: List[Tuple[int, str]], size: int = 900, overlap: int = 150) -> List[dict]:
    """pages: [(nomor_halaman, teks)] -> [{content, page_number, section, chunk_index}]"""
    out, idx = [], 0
    for page_no, text in pages:
        section = None
        for line in text.splitlines():
            if _HEADING.match(line.strip()):
                section = line.strip().lstrip("# ")[:100]
                break
        for piece in _split_text(text, size, overlap):
            out.append({"content": piece, "page_number": page_no, "section": section, "chunk_index": idx})
            idx += 1
    return out
