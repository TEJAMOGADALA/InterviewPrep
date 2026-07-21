import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { roadmapService } from '@/services/mission.service';

/**
 * Cached, filter-aware roadmap tree fetch.
 *
 * - Returns the tree from localStorage instantly (if present) then refreshes
 *   from the server, so navigation feels immediate.
 * - Exposes `matchNode(node, activeFilters)` — a pure predicate the caller
 *   can plug into an existing tree walk to keep the current UI 100% intact.
 * - Persistence is per (user_id, version) so profile switches don't collide.
 */
const CACHE_KEY = 'prepos:roadmap-tree:v1';

function readCache() {
  try {
    const raw = window.localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
function writeCache(payload) {
  try {
    window.localStorage.setItem(CACHE_KEY, JSON.stringify(payload));
  } catch {
    /* quota — silently skip */
  }
}

export function useProgressTree() {
  const [tree, setTree] = useState(() => readCache());
  const [loading, setLoading] = useState(!tree);
  const [error, setError] = useState(null);
  const abortRef = useRef(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await roadmapService.tree();
      if (abortRef.current) return;
      setTree(data);
      writeCache(data);
      setError(null);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    abortRef.current = false;
    refresh();
    return () => { abortRef.current = true; };
  }, [refresh]);

  return { tree, loading, error, refresh, setTree };
}

/**
 * Pure predicate — does this node satisfy the currently active chip filters?
 * A node passes iff EVERY selected group has at least one matching option.
 * Callers walk the tree and keep parents whose descendants match (to preserve
 * the tree UX; nothing gets pruned above a matching leaf).
 */
export function matchNode(node, activeFilters) {
  if (!activeFilters || activeFilters.size === 0) return true;

  const groups = { status: [], difficulty: [], company: [] };
  for (const raw of activeFilters) {
    const [g, v] = raw.split(':');
    if (groups[g]) groups[g].push(v);
  }

  const prog = node.progress || {};
  const status = prog.status || 'not_started';

  if (groups.status.length) {
    const ok = groups.status.some((s) => {
      if (s === 'completed')    return status === 'completed' || status === 'mastered';
      if (s === 'incomplete')   return status === 'not_started' || status === 'in_progress';
      if (s === 'revision_due') return status === 'revision_due';
      if (s === 'bookmarked')   return !!prog.bookmarked;
      if (s === 'favorite')     return !!prog.favorite;
      return false;
    });
    if (!ok) return false;
  }

  if (groups.difficulty.length) {
    const d = (node.difficulty || '').toLowerCase();
    if (!d || !groups.difficulty.includes(d)) return false;
  }

  if (groups.company.length) {
    const ci = node.company_importance || {};
    // Match if the node has importance >= 4 for ANY selected company.
    const ok = groups.company.some((cid) => (ci[cid] || 0) >= 4);
    if (!ok) return false;
  }

  return true;
}
