import { useRoadmapTree } from '@/queries/hooks';

/**
 * useProgressTree (RC1.3.4)
 *
 * Backwards-compatible shim over the RC1.3.2B React Query hook
 * `useRoadmapTree`. The previous implementation kept its own
 * `localStorage` cache under a GLOBAL key, which was a cross-user
 * cache leak (Part K) that RC1.3.3's user-scoped React Query keys
 * had already fixed for every other reader. This file now delegates
 * so KnowledgeBase inherits user isolation for free.
 *
 * The `setTree` / `refresh` returns are preserved (as no-ops that
 * delegate to React Query's `refetch`) so any external caller
 * relying on the legacy signature keeps compiling.
 */
export function useProgressTree() {
  const { data, isLoading, error, refetch } = useRoadmapTree();
  return {
    tree: data || null,
    loading: isLoading,
    error,
    refresh: refetch,
    setTree: () => {
      /* no-op — React Query owns the cache now.
         Consumers that want to mutate should use the appropriate
         mutation hook (useSetNodeStatus, useToggleBookmark, …) or
         call qc.setQueryData through a queryClient reference. */
    },
  };
}

/**
 * Pure predicate — does this node satisfy the currently active chip filters?
 *
 * RC1.3.4 adds the `mastered`, `in_progress` and `weak` status keys so
 * the workspace can reuse the identical predicate the tree view uses.
 * All previously supported keys still work unchanged.
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
  const confidence = prog.confidence || 0;
  const weakness = prog.weakness_score || 0;
  const attempted = (prog.attempts || 0) > 0 || status !== 'not_started';

  if (groups.status.length) {
    const ok = groups.status.some((s) => {
      if (s === 'completed')    return status === 'completed' || status === 'mastered';
      if (s === 'mastered')     return status === 'mastered';
      if (s === 'in_progress')  return status === 'in_progress';
      if (s === 'incomplete')   return status === 'not_started' || status === 'in_progress';
      if (s === 'revision_due') return status === 'revision_due';
      if (s === 'bookmarked')   return !!prog.bookmarked;
      if (s === 'favorite')     return !!prog.favorite;
      if (s === 'weak') {
        return attempted && (
          (confidence > 0 && confidence < 4)
          || weakness >= 50
          || status === 'revision_due'
        );
      }
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
