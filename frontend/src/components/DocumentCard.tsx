import type { DocumentItem } from "../types";

const COLOR: Record<string, string> = { READY: "ok", PROCESSING: "warn", UPLOADED: "warn", FAILED: "err" };

export default function DocumentCard({ doc, canManage, onDelete, onReindex }: {
  doc: DocumentItem; canManage: boolean; onDelete: () => void; onReindex: () => void;
}) {
  return (
    <div className="card doc">
      <div className="doc-head">
        <b title={doc.filename}>{doc.filename}</b>
        <span className={`status ${COLOR[doc.status]}`}>{doc.status}</span>
      </div>
      <div className="muted small">
        .{doc.file_type} · akses {doc.access_level} · {doc.page_count} hlm · {doc.chunk_count} chunk{doc.used_ocr ? " · OCR" : ""}
      </div>
      {doc.error && <div className="err-text small">{doc.error}</div>}
      {canManage && (
        <div className="row">
          <button className="btn small" onClick={onReindex}>Index ulang</button>
          <button className="btn small danger" onClick={onDelete}>Hapus</button>
        </div>
      )}
    </div>
  );
}
