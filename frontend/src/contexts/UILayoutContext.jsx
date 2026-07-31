import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const UILayoutContext = createContext(null);

const STORAGE_KEY = 'prepos:sidebar-collapsed';

export function UILayoutProvider({ children }) {
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false;
    try { return window.localStorage.getItem(STORAGE_KEY) === '1'; }
    catch { return false; }
  });

  useEffect(() => {
    try { window.localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0'); }
    catch {}
  }, [collapsed]);

  const toggle = useCallback(() => setCollapsed((v) => !v), []);

  const value = useMemo(() => ({
    sidebarCollapsed: collapsed,
    setSidebarCollapsed: setCollapsed,
    toggleSidebar: toggle,
  }), [collapsed, toggle]);

  return (
    <UILayoutContext.Provider value={value}>
      {children}
    </UILayoutContext.Provider>
  );
}

export function useUILayout() {
  const ctx = useContext(UILayoutContext);
  if (!ctx) throw new Error('useUILayout must be used within UILayoutProvider');
  return ctx;
}
