import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "../types";

export default function ChatWindow({ messages, busy }: { messages: ChatMessage[]; busy: boolean }) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [messages, busy]);
  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="empty">
          <h2>Apa yang ingin Anda ketahui?</h2>
          <p className="muted">Contoh: “Apa prosedur reimbursement?” · “Berapa total penjualan per cabang bulan Agustus?” · “Analisis penjualan September dan jelaskan penyebab penurunannya”</p>
        </div>
      )}
      {messages.map((m, i) => (
        <div key={i} className={`bubble ${m.role}`}>
          <ReactMarkdown>{m.content || "…"}</ReactMarkdown>
          {!!m.tools_used?.length && (
            <div className="chips">{m.tools_used.map((t) => <span key={t} className="chip tool">🔧 {t}</span>)}</div>
          )}
          {!!m.sources?.length && (
            <div className="chips">
              {m.sources.map((s, j) => <span key={j} className="chip" title={s.snippet}>📎 {s.ref ? `[${s.ref}] ` : ""}{s.document} · hlm. {s.page}</span>)}
            </div>
          )}
        </div>
      ))}
      {busy && messages[messages.length - 1]?.content === "" && <div className="muted small">AI sedang berpikir…</div>}
      <div ref={end} />
    </div>
  );
}
