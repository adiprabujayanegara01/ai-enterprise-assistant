"""LLM Gateway: satu-satunya pintu ke provider LLM. Frontend tidak pernah memanggil LLM langsung.
Mendukung API OpenAI-compatible (OpenAI, Ollama, vLLM, Groq, ...) dan mode `mock` untuk demo tanpa API key."""
import json
import re
import time
from typing import Iterator, List, Optional

import httpx

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import AIUsage


class LLMService:
    @property
    def is_mock(self) -> bool:
        if settings.llm_provider != "openai":
            return True
        local = any(h in settings.openai_base_url for h in ("localhost", "127.0.0.1", "host.docker.internal", "ollama"))
        return not settings.openai_api_key and not local

    # ---------- public API ----------
    def chat(self, messages: List[dict], tools: Optional[List[dict]] = None, temperature: float = 0.2,
             user_id: Optional[int] = None, purpose: str = "chat", json_mode: bool = False) -> dict:
        t0 = time.perf_counter()
        if self.is_mock:
            content = self._mock(messages)
            usage = {"prompt_tokens": sum(len(m.get("content") or "") for m in messages) // 4,
                     "completion_tokens": len(content) // 4}
            self._log(user_id, "mock", purpose, usage, time.perf_counter() - t0)
            return {"content": content, "tool_calls": [], "raw_tool_calls": None}
        body = {"model": settings.llm_model, "messages": messages, "temperature": temperature}
        if tools:
            body["tools"] = [{"type": "function", "function": t} for t in tools]
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        r = httpx.post(f"{settings.openai_base_url.rstrip('/')}/chat/completions", headers=self._headers(),
                       json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        msg = data["choices"][0]["message"]
        raw_calls = msg.get("tool_calls") or None
        calls = []
        for tc in raw_calls or []:
            try:
                args = json.loads(tc["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append({"id": tc["id"], "name": tc["function"]["name"], "arguments": args})
        self._log(user_id, settings.llm_model, purpose, data.get("usage") or {}, time.perf_counter() - t0)
        return {"content": msg.get("content") or "", "tool_calls": calls, "raw_tool_calls": raw_calls}

    def stream(self, messages: List[dict], user_id: Optional[int] = None, temperature: float = 0.2) -> Iterator[str]:
        t0 = time.perf_counter()
        if self.is_mock:
            text = self._mock(messages)
            for w in re.findall(r"\S+\s*", text):
                time.sleep(0.012)
                yield w
            self._log(user_id, "mock", "chat_stream", {"prompt_tokens": 0, "completion_tokens": len(text) // 4},
                      time.perf_counter() - t0)
            return
        body = {"model": settings.llm_model, "messages": messages, "temperature": temperature, "stream": True}
        out_chars = 0
        with httpx.stream("POST", f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                          headers=self._headers(), json=body, timeout=120) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    delta = json.loads(payload)["choices"][0]["delta"].get("content")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                if delta:
                    out_chars += len(delta)
                    yield delta
        prompt_chars = sum(len(m.get("content") or "") for m in messages)
        self._log(user_id, settings.llm_model, "chat_stream",
                  {"prompt_tokens": prompt_chars // 4, "completion_tokens": out_chars // 4}, time.perf_counter() - t0)

    # ---------- internals ----------
    def _headers(self):
        h = {"Content-Type": "application/json"}
        if settings.openai_api_key:
            h["Authorization"] = f"Bearer {settings.openai_api_key}"
        return h

    def _log(self, user_id, model, purpose, usage: dict, latency: float):
        pt, ct = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
        cost = (pt * settings.price_per_1m_input + ct * settings.price_per_1m_output) / 1_000_000
        try:
            with SessionLocal() as db:
                db.add(AIUsage(user_id=user_id, model=model, purpose=purpose, prompt_tokens=pt,
                               completion_tokens=ct, total_tokens=pt + ct, latency=round(latency, 3),
                               estimated_cost=round(cost, 6)))
                db.commit()
        except Exception:
            pass

    def _mock(self, messages: List[dict]) -> str:
        """Jawaban ekstraktif sederhana agar seluruh pipeline RAG tetap bisa didemokan tanpa API key."""
        last = messages[-1].get("content") or ""
        m = re.search(r"<context>(.*?)</context>", last, re.S)
        if m:
            ctx = m.group(1).strip()
            if not ctx or "NO_CONTEXT" in ctx:
                return "Informasi tersebut tidak tersedia pada dokumen yang telah diindeks."
            blocks = re.findall(r"\[S(\d+)\][^\n]*\n(.*?)(?=\n\[S\d+\]|\Z)", ctx, re.S)[:3]
            lines = []
            for n, body in blocks:
                snippet = re.sub(r"\s+", " ", body).strip()[:420]
                lines.append(f"- {snippet} [S{n}]")
            return ("Berdasarkan dokumen perusahaan yang ditemukan:\n\n" + "\n".join(lines) +
                    "\n\n_(Mode demo tanpa LLM: jawaban diambil langsung dari dokumen. "
                    "Set LLM_PROVIDER=openai dan OPENAI_API_KEY untuk jawaban naratif.)_")
        return ("Mode demo aktif (LLM belum dikonfigurasi). Atur LLM_PROVIDER=openai dan OPENAI_API_KEY "
                "pada file .env untuk mengaktifkan LLM penuh.")


llm = LLMService()
