import { ChangeEvent, useCallback, useEffect, useState } from "react";
import DocumentCard from "../components/DocumentCard";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { DocumentItem, Role } from "../types";

export default function Documents() {
  const { can } = useAuth();
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [level, setLevel] = useState<Role>("EMPLOYEE");
  const [msg, setMsg] = useState("");
  const [invoice, setInvoice] = useState<any>(null);
  const load = useCallback(() => api<DocumentItem[]>("/documents").then(setDocs).catch((e) => setMsg(e.message)), []);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {  // polling selama ada dokumen yang masih diproses
    if (!docs.some((d) => d.status === "UPLOADED" || d.status === "PROCESSING")) return;
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, [docs, load]);

  async function upload(e: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    for (const file of files) {
      const form = new FormData(); form.append("file", file); form.append("access_level", level);
      try { await api("/documents/upload", { form }); setMsg(`Mengunggah ${file.name}…`); } catch (ex) { setMsg((ex as Error).message); }
    }
    e.target.value = ""; load();
  }
  async function extractInvoice(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]; if (!file) return;
    const form = new FormData(); form.append("file", file);
    setInvoice({ loading: true });
    try { setInvoice(await api("/documents/extract-invoice", { form })); } catch (ex) { setInvoice({ error: (ex as Error).message }); }
    e.target.value = "";
  }

  return (
    <div className="page">
      <h1>Document Management</h1>
      {can("MANAGER") ? (
        <div className="card row">
          <label className="btn primary">⬆ Upload dokumen
            <input type="file" hidden multiple accept=".pdf,.docx,.xlsx,.csv,.txt,.png,.jpg,.jpeg" onChange={upload} />
          </label>
          <span className="muted small">Level akses:</span>
          <select value={level} onChange={(e) => setLevel(e.target.value as Role)}>
            <option value="EMPLOYEE">EMPLOYEE (semua)</option><option value="MANAGER">MANAGER+</option>{can("ADMIN") && <option value="ADMIN">ADMIN saja</option>}
          </select>
          <span className="muted small">{msg || "PDF, DOCX, XLSX, CSV, TXT, PNG/JPG (OCR otomatis) — maks. 25 MB"}</span>
        </div>
      ) : <div className="card muted">Upload dokumen membutuhkan peran MANAGER atau ADMIN.</div>}
      <div className="grid3">
        {docs.map((d) => (
          <DocumentCard key={d.id} doc={d} canManage={can("MANAGER")}
            onDelete={async () => { if (confirm(`Hapus ${d.filename}?`)) { await api(`/documents/${d.id}`, { method: "DELETE" }); load(); } }}
            onReindex={async () => { await api(`/documents/${d.id}/index`, { method: "POST" }); load(); }} />
        ))}
      </div>
      <div className="card">
        <h3>🧾 Ekstraksi Invoice (OCR → JSON)</h3>
        <p className="muted small">Unggah foto/scan invoice untuk diubah menjadi data terstruktur. File tidak disimpan.</p>
        <input type="file" accept=".png,.jpg,.jpeg,.pdf" onChange={extractInvoice} />
        {invoice?.loading && <p className="muted">Memproses OCR…</p>}
        {invoice?.error && <p className="err-text">{invoice.error}</p>}
        {invoice?.extracted && <pre>{JSON.stringify(invoice.extracted, null, 2)}</pre>}
      </div>
    </div>
  );
}
