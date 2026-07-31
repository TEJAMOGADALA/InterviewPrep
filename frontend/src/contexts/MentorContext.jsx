import React, { createContext, useContext } from 'react';
import useMentorHook from '@/hooks/useMentor';

/**
 * MentorProvider (RC1.3)
 *
 * Wraps a single `useMentor()` instance and exposes it through context so the
 * top-level AI Mentor drawer AND the full-page /app/ai-mentor screen share the
 * same conversation state. This ensures:
 *   • Opening the drawer on any page keeps the last conversation intact.
 *   • Navigating between pages doesn't reset the chat.
 *   • Expanding drawer → full page transitions seamlessly.
 */
const MentorContext = createContext(null);

export function MentorProvider({ children }) {
  const mentor = useMentorHook();
  return (
    <MentorContext.Provider value={mentor}>
      {children}
    </MentorContext.Provider>
  );
}

export function useMentorContext() {
  const ctx = useContext(MentorContext);
  // If a consumer is used outside the provider (e.g. during isolated tests),
  // fall back to a local instance to avoid crashes.
  if (!ctx) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return useMentorHook();
  }
  return ctx;
}
