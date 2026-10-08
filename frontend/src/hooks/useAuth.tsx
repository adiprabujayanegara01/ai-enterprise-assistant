import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { api, getToken, login as apiLogin, register as apiRegister, setToken } from "../services/api";
import type { Role, User } from "../types";

interface Ctx {
  user: User | null; loading: boolean;
  login: (e: string, p: string) => Promise<void>; register: (n: string, e: string, p: string) => Promise<void>;
  logout: () => void; can: (min: Role) => boolean;
}
const RANK: Record<Role, number> = { EMPLOYEE: 1, MANAGER: 2, ADMIN: 3 };
const AuthCtx = createContext<Ctx>(null!);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(!!getToken());
  useEffect(() => {
    if (!getToken()) return;
    api<User>("/auth/me").then(setUser).catch(() => setToken(null)).finally(() => setLoading(false));
  }, []);
  const value: Ctx = {
    user, loading,
    login: async (e, p) => setUser(await apiLogin(e, p)),
    register: async (n, e, p) => setUser(await apiRegister(n, e, p)),
    logout: () => { setToken(null); setUser(null); },
    can: (min) => !!user && RANK[user.role] >= RANK[min],
  };
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}
