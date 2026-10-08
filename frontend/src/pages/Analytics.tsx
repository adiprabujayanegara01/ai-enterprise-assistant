import { useEffect, useState } from "react";
import { ForecastLine, Kpi } from "../components/Chart";
import { api, rupiah } from "../services/api";
import type { AnomalyResult, ForecastResult } from "../types";

export default function Analytics() {
  const [fc, setFc] = useState<ForecastResult | null>(null);
  const [an, setAn] = useState<AnomalyResult | null>(null);
  const [horizon, setHorizon] = useState(30);
  useEffect(() => { api<ForecastResult>(`/analytics/forecast?horizon=${horizon}`).then(setFc).catch(() => {}); }, [horizon]);
  useEffect(() => { api<AnomalyResult>("/analytics/anomalies").then(setAn).catch(() => {}); }, []);

  return (
    <div className="page">
      <h1>Machine Learning Analytics</h1>
      <div className="card">
        <div className="row"><h3>Sales Forecasting</h3>
          <select value={horizon} onChange={(e) => setHorizon(+e.target.value)}>{[14, 30, 60, 90].map((h) => <option key={h} value={h}>{h} hari</option>)}</select></div>
        {fc && !fc.error ? (<>
          <div className="grid4">
            <Kpi title="TOTAL FORECAST" value={rupiah(fc.total_forecast)} />
            <Kpi title="MAPE (hold-out)" value={`${fc.metrics.mape}%`} />
            <Kpi title="MAE" value={rupiah(fc.metrics.mae)} sub={`baseline naive ${rupiah(fc.metrics.baseline_mae_naive_lag7)}`} />
            <Kpi title="RMSE" value={rupiah(fc.metrics.rmse)} />
          </div>
          <ForecastLine history={fc.history} forecast={fc.forecast} />
        </>) : <div className="muted">{fc?.error ?? "Menghitung…"}</div>}
      </div>
      <div className="grid2">
        <div className="card"><h3>Anomali harian ({an?.daily.length ?? 0})</h3>
          <table><thead><tr><th>Tanggal</th><th>Total</th><th>Tx</th><th>z</th></tr></thead><tbody>
            {an?.daily.map((d) => <tr key={d.date}><td>{d.date}</td><td>{rupiah(d.total)}</td><td>{d.transactions}</td><td className={d.z_score < 0 ? "err-text" : "ok-text"}>{d.z_score}</td></tr>)}
          </tbody></table></div>
        <div className="card"><h3>Transaksi tidak wajar ({an?.transaction_anomaly_count ?? 0})</h3>
          <table><thead><tr><th>Tgl</th><th>Produk</th><th>Cabang</th><th>Qty</th><th>Total</th></tr></thead><tbody>
            {an?.transactions.map((t) => <tr key={t.id}><td>{t.date}</td><td>{t.product}</td><td>{t.branch}</td><td>{t.quantity}</td><td>{rupiah(t.total_amount)}</td></tr>)}
          </tbody></table></div>
      </div>
    </div>
  );
}
