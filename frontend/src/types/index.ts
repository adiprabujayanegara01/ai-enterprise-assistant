export type Role = "ADMIN" | "MANAGER" | "EMPLOYEE";
export interface User { id: number; name: string; email: string; role: Role }
export interface Source { ref?: string; document: string; page: number; section?: string | null; snippet?: string }
export interface ChatMessage { id?: number; role: "user" | "assistant"; content: string; sources?: Source[]; tools_used?: string[] }
export interface Conversation { id: number; title: string; updated_at: string }
export interface DocumentItem {
  id: number; filename: string; file_type: string; status: "UPLOADED" | "PROCESSING" | "READY" | "FAILED";
  error?: string | null; access_level: Role; used_ocr: boolean; page_count: number; chunk_count: number; created_at: string;
}
export interface Breakdown { name: string; current: number; previous: number; growth_pct: number | null }
export interface SalesReport {
  label: string; year: number; month: number; growth_pct: number | null; transactions_growth_pct: number | null;
  current: { total: number; transactions: number; customers: number; label: string };
  previous: { total: number; transactions: number; customers: number; label: string };
  by_category: Breakdown[]; by_branch: Breakdown[]; top_products: Breakdown[]; anomaly_count: number;
}
export interface MonthlyPoint { month: string; total: number; transactions: number }
export interface ForecastResult {
  history: { date: string; value: number }[]; forecast: { date: string; value: number }[];
  metrics: { mae: number; rmse: number; mape: number; baseline_mae_naive_lag7: number; holdout_days: number };
  total_forecast: number; model: string; error?: string;
}
export interface AnomalyResult {
  daily: { date: string; total: number; transactions: number; z_score: number; reason: string }[];
  transactions: { id: number; date: string; product: string; branch: string; quantity: number; total_amount: number; score: number }[];
  transaction_anomaly_count: number; method: string;
}
export interface AgentRunSummary { id: number; user_id: number; query: string; tools_used: string[]; status: string; execution_time: number; created_at: string }
export interface AgentRunDetail extends AgentRunSummary {
  answer: string; tool_calls: { tool_name: string; tool_input: unknown; tool_output: string; status: string; duration: number }[];
}
