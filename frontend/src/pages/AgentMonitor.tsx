import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { AgentRunDetail, AgentRunSummary } from "../types";

export default function AgentMonitor() {
  const [runs, setRuns] = useState<AgentRunSummary[]>([]);
  const [detail, setDetail] = useState<AgentRunDetail | null>(null);
  const [tools, setTools] = useState<{ name: string; description: string; min_role: string; allowed: boolean }[]>([]);
  const load = () => api<AgentRunSummary[]>("/agent/runs").then(setRuns).catch(() => {});
  useEffect(() => { load(); api("/agent/tools").then(setTools).catch(() => {}); }, []);

  return (
    <div className="page">
      <h1>Agent Monitor</h1>
      <div className="card"><h3>Tools tersedia</h3>
        <div className="chips">{tools.map((t) => <span key={t.name} className={`chip ${t.allowed ? "tool" : "off"}`} title={t.description}>{t.allowed ? "🔧" : "🔒"} {t.name} · {t.min_role}</span>)}</div></div>
      <div className="grid2">
        <div className="card"><div className="row"><h3>Riwayat eksekusi</h3><button className="btn small" onClick={load}>Refresh</button></div>
          <table><thead><tr><th>#</th><th>Query</th><th>Tools</th><th>Status</th><th>Waktu</th></tr></thead><tbody>
            {runs.map((r) => (
              <tr key={r.id} className="click" onClick={async () => setDetail(await api<AgentRunDetail>(`/agent/runs/${r.id}`))}>
                <td>{r.id}</td><td>{r.query.slice(0, 50)}</td><td>{r.tools_used.length}</td>
                <td><span className={`status ${r.status === "COMPLETED" ? "ok" : "err"}`}>{r.status}</span></td><td>{r.execution_time}s</td>
              </tr>))}
          </tbody></table></div>
        <div className="card"><h3>Detail eksekusi</h3>
          {!detail ? <div className="muted">Pilih satu run untuk melihat tool calls.</div> : (<>
            <p><b>Query:</b> {detail.query}</p>
            {detail.tool_calls.map((t, i) => (
              <details key={i}><summary>{i + 1}. {t.tool_name} <span className={`status ${t.status === "OK" ? "ok" : "err"}`}>{t.status}</span> · {t.duration}s</summary>
                <pre>{JSON.stringify(t.tool_input)}</pre><pre>{t.tool_output.slice(0, 1500)}</pre></details>))}
            <p><b>Jawaban:</b></p><pre>{detail.answer}</pre></>)}
        </div>
      </div>
    </div>
  );
}
