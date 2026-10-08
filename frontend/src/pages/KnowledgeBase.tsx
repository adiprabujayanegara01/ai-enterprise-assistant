import { FormEvent, useState } from "react";
import { api } from "../services/api";

interface Hit { document: string; page: number; section?: string; score: number; content: string }

export default function KnowledgeBase() {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[] | null>(null);
  const [err, setErr] = useState("");
  async function search(e: FormEvent) {
    e.preventDefault(); setErr("");
    try { setHits(await api<Hit[]>(`/documents/search?q=${encodeURIComponent(q)}`)); } catch (ex) { setErr((ex as Error).message); }
  }
  return (
    <div className="page">
      <h1>Knowledge Base</h1>
      <p className="muted">Pencarian semantik + keyword (hybrid search, pgvector) pada seluruh dokumen yang boleh Anda akses.</p>
      <form className="composer" onSubmit={search}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Cari: batas waktu reimbursement, cuti melahirkan…" />
        <button className="btn primary" disabled={q.length < 2}>Cari</button>
      </form>
      {err && <div className="err-text">{err}</div>}
      {hits?.length === 0 && <div className="muted">Tidak ada hasil.</div>}
      {hits?.map((h, i) => (
        <div key={i} className="card">
          <b>{h.document}</b> <span className="muted small">· hlm. {h.page}{h.section ? ` · ${h.section}` : ""} · skor {h.score}</span>
          <p>{h.content}</p>
        </div>
      ))}
    </div>
  );
}
