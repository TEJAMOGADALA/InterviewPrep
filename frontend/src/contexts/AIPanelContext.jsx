import { createContext, useContext, useState } from 'react';

const AIPanelContext = createContext(null);

export function AIPanelProvider({ children }) {
  const [open, setOpen] = useState(false);
  const toggle = () => setOpen((v) => !v);
  return (
    <AIPanelContext.Provider value={{ open, setOpen, toggle }}>
      {children}
    </AIPanelContext.Provider>
  );
}

export function useAIPanel() {
  const ctx = useContext(AIPanelContext);
  if (!ctx) throw new Error('useAIPanel must be used within AIPanelProvider');
  return ctx;
}
