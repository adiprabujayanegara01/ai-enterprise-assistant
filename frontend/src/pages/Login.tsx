import { FormEvent, useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ name: "", email: "manager@company.com", password: "Manager123!" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setErr(""); setBusy(true);
    try { mode === "login" ? await login(f.email, f.password) : await register(f.name, f.email, f.password); }
    catch (ex) { setErr((ex as Error).message); } finally { setBusy(false); }
  }
  return (
    <div className="center">
      <form className="card login" onSubmit={submit}>
        <h1>AI Enterprise Assistant</h1>
        <p className="muted">Knowledge, dokumen & analitik bisnis dalam satu asisten.</p>
        {mode === "register" && <input placeholder="Nama lengkap" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} required minLength={2} />}
        <input type="email" placeholder="Email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} required />
        <input type="password" placeholder="Password (min. 8 karakter)" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} required minLength={8} />
        {err && <div className="err-text">{err}</div>}
        <button className="btn primary" disabled={busy}>{busy ? "…" : mode === "login" ? "Masuk" : "Daftar"}</button>
        <button type="button" className="btn ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Belum punya akun? Daftar" : "Sudah punya akun? Masuk"}
        </button>
        {mode === "login" && (
          <div className="muted small demo">
            Akun demo — <a onClick={() => setF({ ...f, email: "admin@company.com", password: "Admin123!" })}>Admin</a> ·{" "}
            <a onClick={() => setF({ ...f, email: "manager@company.com", password: "Manager123!" })}>Manager</a> ·{" "}
            <a onClick={() => setF({ ...f, email: "employee@company.com", password: "Employee123!" })}>Employee</a>
          </div>
        )}
      </form>
    </div>
  );
}
