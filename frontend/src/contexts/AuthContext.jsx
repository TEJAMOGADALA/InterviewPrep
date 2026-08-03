import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { authService } from '@/services/auth.service';

/**
 * AuthContext
 *
 * RC1.3.3 · Cache isolation contract
 * -----------------------------------
 * This provider is the ONE place we enforce the "one user's data
 * never leaks into another user's session" invariant.
 *
 *   • On every login / register — we DO NOT need to clear the cache
 *     because the query keys carry the user id (see queries/keys.js).
 *     User B's `qk.dashboard(B)` is a different cache entry from
 *     User A's `qk.dashboard(A)` — nothing to leak.
 *
 *   • On logout — we call `queryClient.clear()`. This is belt-and-
 *     braces: even the previous user's namespaced entries are
 *     removed so a subsequent session starts from a clean slate.
 *     Rationale: sensitive data (streak, mission, activity) should
 *     not sit in memory once the user has explicitly signed out,
 *     even if the app is not immediately reloaded.
 *
 *   • On user id CHANGE (rare — same tab, different login) — we
 *     ALSO clear the cache to be safe. This catches the pathological
 *     sequence "log in as A → refresh removes A from cache but leaves
 *     query data on disk → log in as B" that some SSR setups exhibit.
 *
 * The `MentorContext` reset is signalled via the `authNonce` value
 * exposed on the context. MentorProvider watches it and drops its
 * state whenever it changes.
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // null = checking; false = logged out; object = logged in
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Monotonic counter that bumps every time a *different* user logs
  // in. Consumers (e.g. MentorContext) watch this to drop local state
  // that predates the current session.
  const [authNonce, setAuthNonce] = useState(0);
  const prevUserIdRef = useRef(null);

  const queryClient = useQueryClient();

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

  // Detect user-id transitions. Two shapes we care about:
  //  1. anon → user     (login)      — no cache to clear (was empty)
  //  2. userA → userB   (same tab)   — clear cache + bump nonce
  //  3. user → anon     (logout)     — clear cache + bump nonce
  useEffect(() => {
    const nextId = user && typeof user === 'object' ? user.id : null;
    const prevId = prevUserIdRef.current;
    if (prevId != null && prevId !== nextId) {
      // A real transition (either to a different user OR to signed-out).
      // Clear ALL cached queries so no stale user-scoped payload can be
      // observed by the incoming session.
      try {
        queryClient.clear();
      } catch {
        // queryClient.clear should never throw, but we swallow just in
        // case a mid-teardown mutation is holding a reference.
      }
      setAuthNonce((n) => n + 1);
    }
    prevUserIdRef.current = nextId;
  }, [user, queryClient]);

  const login = async (email, password) => {
    const u = await authService.login({ email, password });
    setUser(u);
    return u;
  };

  const register = async (name, email, password) => {
    return await authService.register({
        name,
        email,
        password,
    });
  };

  const resendVerification = async (email) => {
  return await authService.resendVerification(email);
  };

  const logout = async () => {
    try { await authService.logout(); } catch { /* network errors on logout are non-fatal */ }
    // Explicit cache clear + user-scoped state reset happens in the
    // effect above via the id-transition detector — we just flip the
    // user state here.
    setUser(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    // Consumers that hold user-scoped React state outside React Query
    // (e.g. useMentor) watch this to drop it on session change.
    authNonce,
    login,
    register,
    resendVerification,
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
