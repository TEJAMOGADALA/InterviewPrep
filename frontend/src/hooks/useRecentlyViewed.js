import { useCallback, useEffect, useMemo, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

/**
 * useRecentlyViewed (RC1.3.4)
 *
 * Lightweight, user-scoped "which topics has this learner opened
 * recently?" store. Deliberately client-only — the signal is a UX
 * convenience, not an authoritative record — so we neither touch the
 * database nor create a new API endpoint for it.
 *
 * Storage
 * -------
 * localStorage key is `prepos:recently-viewed:v1:<userId>`.
 * Because the key embeds the authenticated user id, user A's list is
 * disjoint from user B's list, honouring the same isolation contract
 * as the RC1.3.3 React Query key scheme. Anonymous callers get no
 * persistence.
 *
 * Payload shape
 * -------------
 *   [{ nodeId: string, viewedAt: ISO string }, …]
 *
 * Cap: `LIMIT` most recent entries, newest-first. Duplicates are
 * de-duplicated by node id (the newest timestamp wins).
 *
 * API
 * ---
 *   const { entries, record, clear, contains } = useRecentlyViewed();
 *
 *   record(nodeId)   — insert-or-move-to-front. Safe to call on every
 *                      DeepTopicPage open.
 *   contains(id)     — cheap set-lookup for the Continue Learning
 *                      dedupe.
 *   clear()          — nuke the list (used by a future "clear
 *                      history" action; not wired to any UI today).
 */

const KEY_PREFIX = 'prepos:recently-viewed:v1:';
const LIMIT = 30;

function readList(userId) {
  if (!userId || typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(KEY_PREFIX + userId);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((e) => e && typeof e.nodeId === 'string' && typeof e.viewedAt === 'string')
      .slice(0, LIMIT);
  } catch {
    return [];
  }
}

function writeList(userId, entries) {
  if (!userId || typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(KEY_PREFIX + userId, JSON.stringify(entries.slice(0, LIMIT)));
  } catch {
    /* quota / privacy modes — silently degrade to in-memory only */
  }
}

export function useRecentlyViewed() {
  const { user } = useAuth();
  const userId = user?.id;
  const [entries, setEntries] = useState(() => readList(userId));

  // Reload when the authenticated user changes — the key changes,
  // so the previous user's list is no longer visible.
  useEffect(() => {
    setEntries(readList(userId));
  }, [userId]);

  // Cross-tab sync: another tab bumping the same key should refresh
  // the in-memory copy here so the two tabs stay consistent.
  useEffect(() => {
    if (typeof window === 'undefined' || !userId) return;
    const storageKey = KEY_PREFIX + userId;
    const onStorage = (e) => {
      if (e.key === storageKey) setEntries(readList(userId));
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [userId]);

  const record = useCallback((nodeId) => {
    if (!nodeId || !userId) return;
    setEntries((prev) => {
      const next = [
        { nodeId, viewedAt: new Date().toISOString() },
        ...prev.filter((e) => e.nodeId !== nodeId),
      ].slice(0, LIMIT);
      writeList(userId, next);
      return next;
    });
  }, [userId]);

  const clear = useCallback(() => {
    if (!userId) return;
    writeList(userId, []);
    setEntries([]);
  }, [userId]);

  const idSet = useMemo(() => new Set(entries.map((e) => e.nodeId)), [entries]);
  const contains = useCallback((id) => idSet.has(id), [idSet]);

  return { entries, record, clear, contains };
}
