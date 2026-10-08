import hashlib
import re
from typing import List

import numpy as np

from app.core.config import settings

_TOKEN = re.compile(r"[a-z0-9]+")


def hash_embed(text: str, dim: int) -> List[float]:
    """Embedding deterministik tanpa model eksternal (feature hashing: kata, bigram, char n-gram).
    Cukup baik untuk demo + hybrid search. Untuk kualitas produksi pakai provider 'openai' / 'sentence_transformers'."""
    toks = _TOKEN.findall(text.lower())
    feats = list(toks) + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
    for t in toks:
        p = f"<{t}>"
        feats += [p[i:i + 4] for i in range(max(1, len(p) - 3))]
    v = np.zeros(dim, dtype=np.float32)
    for f in feats:
        h = int.from_bytes(hashlib.blake2b(f.encode(), digest_size=8).digest(), "big")
        v[h % dim] += 1.0 if (h >> 63) & 1 else -1.0
    n = float(np.linalg.norm(v))
    return (v / n).tolist() if n else v.tolist()


class EmbeddingService:
    def __init__(self):
        self._st_model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        p = settings.embedding_provider
        if p == "openai":
            return self._openai(texts)
        if p == "sentence_transformers":
            return self._st(texts)
        return [hash_embed(t, settings.embedding_dim) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def _openai(self, texts):
        import httpx
        out = []
        for i in range(0, len(texts), 64):
            batch = texts[i:i + 64]
            r = httpx.post(
                f"{settings.openai_base_url.rstrip('/')}/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.embedding_model, "input": batch, "dimensions": settings.embedding_dim},
                timeout=60,
            )
            r.raise_for_status()
            out += [d["embedding"] for d in sorted(r.json()["data"], key=lambda d: d["index"])]
        return out

    def _st(self, texts):
        if self._st_model is None:
            from sentence_transformers import SentenceTransformer  # pip install sentence-transformers
            self._st_model = SentenceTransformer(settings.embedding_model)
        return self._st_model.encode(texts, normalize_embeddings=True).tolist()


embeddings = EmbeddingService()
