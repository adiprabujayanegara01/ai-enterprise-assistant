import { useEffect, useState } from "react";
import { ForecastLine, GrowthBars, Kpi, MonthlyBar } from "../components/Chart";
import { api, pct, rupiah } from "../services/api";
import type { ForecastResult, MonthlyPoint, SalesReport } from "../types";

export default function Dashboard() {
  const [rep, setRep] = useState<SalesReport | null>(null);
  const [monthly, setMonthly] = useState<MonthlyPoint[]>([]);
  const [fc, setFc] = useState<ForecastResult | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api<SalesReport>("/analytics/summary").then(setRep).catch((e) => setErr(e.message));
    api<MonthlyPoint[]>("/analytics/monthly").then(setMonthly).catch(() => {});
    api<ForecastResult>("/analytics/forecast?horizon=30").then(setFc).catch(() => {});
  }, []);

  if (err) return <div className="page"><div className="card err-text">{err}</div></div>;
  if (!rep) return <div className="page muted">Memuat dashboard…</div>;
  const tone = (v: number | null) => (v == null ? undefined : v < 0 ? "down" : "up");
  return (
    <div className="page">
      <h1>Business Intelligence — {rep.label}</h1>
      <div className="grid4">
        <Kpi title="TOTAL SALES" value={rupiah(rep.current.total)} sub={`${pct(rep.growth_pct)} vs ${rep.previous.label}`} tone={tone(rep.growth_pct)} />
        <Kpi title="TRANSACTIONS" value={rep.current.transactions.toLocaleString("id-ID")} sub={`${pct(rep.transactions_growth_pct)} vs bulan lalu`} tone={tone(rep.transactions_growth_pct)} />
        <Kpi title="CUSTOMERS" value={rep.current.customers.toLocaleString("id-ID")} />
        <Kpi title="ANOMALIES" value={String(rep.anomaly_count)} sub="transaksi tidak wajar (Isolation Forest)" tone={rep.anomaly_count ? "down" : undefined} />
      </div>
      <div className="grid2">
        <div className="card"><h3>Revenue per bulan</h3><MonthlyBar data={monthly} /></div>
        <div className="card"><h3>Performa cabang (vs bulan lalu)</h3><GrowthBars data={rep.by_branch} /></div>
      </div>
      <div className="grid2">
        <div className="card"><h3>Performa kategori (vs bulan lalu)</h3><GrowthBars data={rep.by_category} /></div>
        <div className="card">
          <h3>Pertumbuhan per segmen</h3>
          <table><thead><tr><th>Segmen</th><th>Saat ini</th><th>Growth</th></tr></thead><tbody>
            {[...rep.by_category, ...rep.by_branch].map((r) => (
              <tr key={r.name}><td>{r.name}</td><td>{rupiah(r.current)}</td><td className={(r.growth_pct ?? 0) < 0 ? "err-text" : "ok-text"}>{pct(r.growth_pct)}</td></tr>
            ))}
          </tbody></table>
        </div>
      </div>
      {fc && !fc.error && (
        <div className="card"><h3>Forecast 30 hari — prediksi {rupiah(fc.total_forecast)}</h3>
          <ForecastLine history={fc.history} forecast={fc.forecast} />
          <div className="muted small">MAPE {fc.metrics.mape}% · MAE {rupiah(fc.metrics.mae)} · baseline naive MAE {rupiah(fc.metrics.baseline_mae_naive_lag7)} · {fc.model}</div>
        </div>
      )}
    </div>
  );
}
