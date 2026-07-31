import { useQuery } from '@tanstack/react-query';
import { dashboardService, missionService, roadmapService } from '@/services/mission.service';
import { qk } from '@/queries/keys';

/**
 * Read-only query hooks.
 *
 * Every hook is a thin wrapper over the existing service — the goal
 * is deduplication + shared invalidation, not a new API surface.
 * Callers keep passing the same data around and rendering the same
 * JSX; only the loading mechanism changes.
 *
 * RC1.3.2B Phase 1: staleTime intentionally follows the QueryClient
 * default (60s from index.js). Phase 2 will tune these individually.
 */

// ---------- Dashboard --------------------------------------------------

/**
 * The canonical dashboard read. Topbar, MissionControl and (Phase 2)
 * CommandAnalytics all subscribe to this same cache entry, so a
 * single mutation propagates everywhere without any extra network
 * round-trip. Duplicate requests within one staleTime window are
 * naturally deduped by React Query.
 */
export function useDashboard(options = {}) {
  return useQuery({
    queryKey: qk.dashboard(),
    queryFn: () => dashboardService.get(),
    ...options,
  });
}

// ---------- Roadmap ----------------------------------------------------

export function useRoadmapTree(options = {}) {
  return useQuery({
    queryKey: qk.roadmapTree(),
    queryFn: () => roadmapService.tree(),
    ...options,
  });
}

export function useRoadmapSummary(options = {}) {
  return useQuery({
    queryKey: qk.roadmapSummary(),
    queryFn: () => roadmapService.summary(),
    ...options,
  });
}

/**
 * Deep node view — the payload behind DeepTopicPage. `enabled: !!nodeId`
 * so the hook can be called unconditionally in a component that
 * receives a nullable route param.
 */
export function useRoadmapNode(nodeId, options = {}) {
  return useQuery({
    queryKey: qk.roadmapNode(nodeId),
    queryFn: () => roadmapService.node(nodeId),
    enabled: !!nodeId,
    ...options,
  });
}
