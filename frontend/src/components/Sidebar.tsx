import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const ITEMS = [
  { to: "/dashboard", label: "📊 Dashboard", min: "MANAGER" },
  { to: "/chat", label: "💬 AI Chat", min: "EMPLOYEE" },
  { to: "/documents", label: "📄 Documents", min: "EMPLOYEE" },
  { to: "/knowledge", label: "🔎 Knowledge Base", min: "EMPLOYEE" },
  { to: "/analytics", label: "📈 Analytics", min: "MANAGER" },
  { to: "/agent", label: "🤖 Agent Monitor", min: "EMPLOYEE" },
] as const;

export default function Sidebar() {
  const { user, logout, can } = useAuth();
  return (
    <aside className="sidebar">
      <div className="brand">AI Enterprise<br /><span>Assistant</span></div>
      <nav>
        {ITEMS.filter((i) => can(i.min)).map((i) => (
          <NavLink key={i.to} to={i.to} className={({ isActive }) => (isActive ? "nav active" : "nav")}>{i.label}</NavLink>
        ))}
      </nav>
      <div className="user">
        <div><b>{user?.name}</b></div>
        <div className="muted small">{user?.email}</div>
        <span className="badge">{user?.role}</span>
        <button className="btn ghost" onClick={logout}>Keluar</button>
      </div>
    </aside>
  );
}
