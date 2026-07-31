import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const ThemeContext = createContext(null);

const STORAGE_KEY = 'prepos:theme';
const VALID = ['light', 'dark', 'system'];

function resolveMode(pref) {
  if (pref === 'system') {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    return 'dark';
  }
  return pref;
}

function applyTheme(mode) {
  const root = document.documentElement;
  if (mode === 'light') {
    root.classList.remove('dark');
    root.classList.add('light');
    root.setAttribute('data-theme', 'light');
  } else {
    root.classList.add('dark');
    root.classList.remove('light');
    root.setAttribute('data-theme', 'dark');
  }
}

export function ThemeProvider({ children }) {
  const [preference, setPreferenceState] = useState(() => {
    if (typeof window === 'undefined') return 'dark';
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return VALID.includes(stored) ? stored : 'dark';
  });

  const [resolved, setResolved] = useState(() => resolveMode(preference));

  // Apply theme whenever it changes, and listen for system changes when in
  // 'system' mode so the UI reacts live.
  useEffect(() => {
    const mode = resolveMode(preference);
    setResolved(mode);
    applyTheme(mode);
    if (preference !== 'system' || typeof window === 'undefined' || !window.matchMedia) return;
    const mql = window.matchMedia('(prefers-color-scheme: light)');
    const handler = () => {
      const m = mql.matches ? 'light' : 'dark';
      setResolved(m);
      applyTheme(m);
    };
    if (mql.addEventListener) mql.addEventListener('change', handler);
    else if (mql.addListener) mql.addListener(handler);
    return () => {
      if (mql.removeEventListener) mql.removeEventListener('change', handler);
      else if (mql.removeListener) mql.removeListener(handler);
    };
  }, [preference]);

  const setPreference = useCallback((next) => {
    if (!VALID.includes(next)) return;
    setPreferenceState(next);
    try { window.localStorage.setItem(STORAGE_KEY, next); } catch {}
  }, []);

  const value = useMemo(() => ({
    theme: preference,
    resolvedTheme: resolved,
    setTheme: setPreference,
    toggle: () => setPreference(resolved === 'dark' ? 'light' : 'dark'),
  }), [preference, resolved, setPreference]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
