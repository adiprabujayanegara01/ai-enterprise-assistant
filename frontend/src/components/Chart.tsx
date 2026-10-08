import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { rupiah } from "../services/api";

export function Kpi({ title, value, sub, tone }: { title: string; value: string; sub?: string; tone?: "up" | "down" }) {
  return (
    <div className="card kpi">
      <div className="muted small">{title}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className={`small ${tone === "down" ? "err-text" : tone === "up" ? "ok-text" : "muted"}`}>{sub}</div>}
    </div>
  );
}

const axis = (v: number) => (v >= 1e9 ? `${(v / 1e9).toFixed(1)}M` : v >= 1e6 ? `${Math.round(v / 1e6)}jt` : String(v));

export function MonthlyBar({ data }: { data: { month: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#2a3350" /><XAxis dataKey="month" stroke="#8b95b3" />
        <YAxis tickFormatter={axis} stroke="#8b95b3" /><Tooltip formatter={(v) => rupiah(Number(v))} contentStyle={{ background: "#151b2e", border: "1px solid #2a3350" }} />
        <Bar dataKey="total" name="Penjualan" fill="#6c8cff" radius={[4, 4, 0, 0]} /></BarChart>
    </ResponsiveContainer>
  );
}

export function GrowthBars({ data }: { data: { name: string; current: number; previous: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#2a3350" /><XAxis dataKey="name" stroke="#8b95b3" fontSize={11} />
        <YAxis tickFormatter={axis} stroke="#8b95b3" /><Tooltip formatter={(v) => rupiah(Number(v))} contentStyle={{ background: "#151b2e", border: "1px solid #2a3350" }} /><Legend />
        <Bar dataKey="previous" name="Bulan lalu" fill="#46507a" radius={[4, 4, 0, 0]} />
        <Bar dataKey="current" name="Bulan ini" fill="#6c8cff" radius={[4, 4, 0, 0]} /></BarChart>
    </ResponsiveContainer>
  );
}

export function ForecastLine({ history, forecast }: { history: { date: string; value: number }[]; forecast: { date: string; value: number }[] }) {
  const data = [...history.map((h) => ({ date: h.date.slice(5), actual: h.value })), ...forecast.map((f) => ({ date: f.date.slice(5), forecast: f.value }))];
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#2a3350" /><XAxis dataKey="date" stroke="#8b95b3" interval={9} />
        <YAxis tickFormatter={axis} stroke="#8b95b3" /><Tooltip formatter={(v) => rupiah(Number(v))} contentStyle={{ background: "#151b2e", border: "1px solid #2a3350" }} /><Legend />
        <Line dataKey="actual" name="Aktual" stroke="#6c8cff" dot={false} strokeWidth={2} />
        <Line dataKey="forecast" name="Forecast" stroke="#ffb454" dot={false} strokeWidth={2} strokeDasharray="5 4" /></LineChart>
    </ResponsiveContainer>
  );
}
