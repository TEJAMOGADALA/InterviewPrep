import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const AIPanelContext = createContext(null);

/**
 * AIPanelProvider (RC1.3)
 *
 * The AI Mentor drawer is now a truly global assistant — it lives above the
 * shell so its open/close state and (via useMentor) its conversation state
 * survive route changes. Behaviours added:
 *   • ESC closes.
 *   • Click-outside closes (the drawer emits its own overlay).
 *   • openWith(prompt, opts) lets any page open the drawer pre-seeded.
 */
export function AIPanelProvider({ children }) {
  const [open, setOpen] = useState(false);
  const [pendingSeed, setPendingSeed] = useState(null);   // { prompt, topicNodeId, responseStyle }

  const toggle = useCallback(() => setOpen((v) => !v), []);
  const close = useCallback(() => setOpen(false), []);

  const openWith = useCallback((prompt = '', opts = {}) => {
    setPendingSeed({ prompt: String(prompt || ''), ...opts });
    setOpen(true);
  }, []);

  const consumeSeed = useCallback(() => {
    const s = pendingSeed;
    setPendingSeed(null);
    return s;
  }, [pendingSeed]);

  // ESC to close
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  const value = useMemo(() => ({
    open, setOpen, toggle, close, openWith, consumeSeed,
  }), [open, toggle, close, openWith, consumeSeed]);

  return (
    <AIPanelContext.Provider value={value}>
      {children}
    </AIPanelContext.Provider>
  );
}

export function useAIPanel() {
  const ctx = useContext(AIPanelContext);
  if (!ctx) throw new Error('useAIPanel must be used within AIPanelProvider');
  return ctx;
}
