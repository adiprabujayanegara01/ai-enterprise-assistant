import { FormEvent, useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import { api, streamChat } from "../services/api";
import type { ChatMessage, Conversation } from "../types";

export default function Chat() {
  const [convs, setConvs] = useState<Conversation[]>([]);
  const [cid, setCid] = useState<number | null>(null);
  const [msgs, setMsgs] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<"rag" | "agent">("rag");
  const [busy, setBusy] = useState(false);

  const loadConvs = () => api<Conversation[]>("/chat/history").then(setConvs).catch(() => {});
  useEffect(() => { loadConvs(); }, []);

  async function open(id: number) {
    const c = await api(`/chat/${id}`); setCid(id); setMsgs(c.messages);
  }
  async function remove(id: number) {
    await api(`/chat/${id}`, { method: "DELETE" });
    if (cid === id) { setCid(null); setMsgs([]); }
    loadConvs();
  }
  const patchLast = (fn: (m: ChatMessage) => ChatMessage) => setMsgs((p) => p.map((m, i) => (i === p.length - 1 ? fn(m) : m)));

  async function send(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput(""); setBusy(true);
    setMsgs((p) => [...p, { role: "user", content: text }, { role: "assistant", content: "" }]);
    try {
      if (mode === "agent") {
        const r = await api("/chat", { body: { message: text, conversation_id: cid, mode: "agent" } });
        setCid(r.conversation_id);
        patchLast((m) => ({ ...m, content: r.answer, tools_used: r.tools_used }));
      } else {
        await streamChat(text, cid, {
          meta: setCid,
          token: (t) => patchLast((m) => ({ ...m, content: m.content + t })),
          sources: (s) => patchLast((m) => ({ ...m, sources: s })),
        });
      }
    } catch (ex) {
      patchLast((m) => ({ ...m, content: `⚠️ ${(ex as Error).message}` }));
    } finally { setBusy(false); loadConvs(); }
  }

  return (
    <div className="chat-layout">
      <div className="conv-list">
        <button className="btn primary" onClick={() => { setCid(null); setMsgs([]); }}>+ Percakapan baru</button>
        {convs.map((c) => (
          <div key={c.id} className={`conv ${c.id === cid ? "active" : ""}`} onClick={() => open(c.id)}>
            <span>{c.title}</span><a onClick={(e) => { e.stopPropagation(); remove(c.id); }}>✕</a>
          </div>
        ))}
      </div>
      <div className="chat-main">
        <div className="mode">
          <button className={mode === "rag" ? "tab active" : "tab"} onClick={() => setMode("rag")}>📚 Tanya Dokumen (RAG)</button>
          <button className={mode === "agent" ? "tab active" : "tab"} onClick={() => setMode("agent")}>🤖 Agent (SQL + RAG + ML)</button>
        </div>
        <ChatWindow messages={msgs} busy={busy} />
        <form className="composer" onSubmit={send}>
          <input value={input} onChange={(e) => setInput(e.target.value)} disabled={busy}
            placeholder={mode === "rag" ? "Tanya tentang SOP, kebijakan, laporan…" : "Minta analisis, query data penjualan, forecast…"} />
          <button className="btn primary" disabled={busy || !input.trim()}>Kirim</button>
        </form>
      </div>
    </div>
  );
}
