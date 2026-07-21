import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { authService } from '@/services/auth.service';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // null = checking; false = logged out; object = logged in
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkSession = useCallback(async () => {
    try {
      const me = await authService.me();
      setUser(me);
    } catch {
      setUser(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  const login = async (email, password) => {
    const u = await authService.login({ email, password });
    setUser(u);
    return u;
  };

  const register = async (name, email, password) => {
    const u = await authService.register({ name, email, password });
    setUser(u);
    return u;
  };

  const logout = async () => {
    try { await authService.logout(); } catch {}
    setUser(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refresh: checkSession,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
