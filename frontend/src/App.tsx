import { ReactElement } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import { useAuth } from "./hooks/useAuth";
import AgentMonitor from "./pages/AgentMonitor";
import Analytics from "./pages/Analytics";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import KnowledgeBase from "./pages/KnowledgeBase";
import Login from "./pages/Login";
import type { Role } from "./types";

function Protected({ children, min = "EMPLOYEE" }: { children: ReactElement; min?: Role }) {
  const { user, loading, can } = useAuth();
  if (loading) return <div className="center muted">Memuat…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!can(min)) return <div className="page"><div className="card">Halaman ini membutuhkan peran {min}.</div></div>;
  return <div className="layout"><Sidebar /><main className="main">{children}</main></div>;
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/" element={<Protected><Navigate to={user && user.role !== "EMPLOYEE" ? "/dashboard" : "/chat"} replace /></Protected>} />
      <Route path="/dashboard" element={<Protected min="MANAGER"><Dashboard /></Protected>} />
      <Route path="/chat" element={<Protected><Chat /></Protected>} />
      <Route path="/documents" element={<Protected><Documents /></Protected>} />
      <Route path="/knowledge" element={<Protected><KnowledgeBase /></Protected>} />
      <Route path="/analytics" element={<Protected min="MANAGER"><Analytics /></Protected>} />
      <Route path="/agent" element={<Protected><AgentMonitor /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
