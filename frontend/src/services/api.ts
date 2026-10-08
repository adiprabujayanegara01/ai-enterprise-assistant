import type { User } from "../types";

const TOKEN_KEY = "aea_token";
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string | null) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY));

async function handle(res: Response) {
  if (res.status === 401) { setToken(null); if (!location.pathname.endsWith("/login")) location.href = "/login"; }
  if (!res.ok) {
    let msg = res.statusText;
    try { const j = await res.json(); msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail); } catch { /* ignore */ }
    throw new Error(msg);
  }
  return res.status === 204 ? null : res.json();
}

export async function api<T = any>(path: string, opts: { method?: string; body?: unknown; form?: FormData } = {}): Promise<T> {
  const headers: Record<string, string> = {};
  const t = getToken();
  if (t) headers.Authorization = `Bearer ${t}`;
  if (opts.body) headers["Content-Type"] = "application/json";
  const res = await fetch(`/api${path}`, {
    method: opts.method ?? (opts.body || opts.form ? "POST" : "GET"), headers,
    body: opts.form ?? (opts.body ? JSON.stringify(opts.body) : undefined),
  });
  return handle(res);
}

export async function login(email: string, password: string): Promise<User> {
  const r = await api("/auth/login", { body: { email, password } });
  setToken(r.access_token);
  return r.user;
}
export async function register(name: string, email: string, password: string): Promise<User> {
  const r = await api("/auth/register", { body: { name, email, password } });
  setToken(r.access_token);
  return r.user;
}

/** Streaming chat via Server-Sent Events (fetch + ReadableStream, agar bisa mengirim header Authorization). */
export async function streamChat(
  message: string, conversationId: number | null,
  on: { meta?: (id: number) => void; token: (t: string) => void; sources?: (s: any[]) => void },
) {
  const res = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${getToken()}` },
    body: JSON.stringify({ message, conversation_id: conversationId, mode: "rag" }),
  });
  if (!res.ok || !res.body) await handle(res);
  const reader = res.body!.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i: number;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const block = buf.slice(0, i); buf = buf.slice(i + 2);
      const ev = /^event: (.+)$/m.exec(block)?.[1];
      const data = /^data: (.+)$/m.exec(block)?.[1];
      if (!ev || data === undefined) continue;
      const payload = JSON.parse(data);
      if (ev === "meta") on.meta?.(payload.conversation_id);
      else if (ev === "token") on.token(payload);
      else if (ev === "sources") on.sources?.(payload);
    }
  }
}

export const rupiah = (v: number) =>
  Math.abs(v) >= 1e9 ? `Rp${(v / 1e9).toFixed(2).replace(".", ",")} M`
  : Math.abs(v) >= 1e6 ? `Rp${(v / 1e6).toFixed(1).replace(".", ",")} jt` : `Rp${Math.round(v).toLocaleString("id-ID")}`;
export const pct = (v: number | null | undefined) => (v == null ? "-" : `${v > 0 ? "+" : ""}${v.toFixed(1)}%`);
