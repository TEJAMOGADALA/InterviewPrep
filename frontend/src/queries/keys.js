/**
 * Central React Query key catalogue.
 *
 * Single source of truth so every hook/component references the same
 * key strings. This is what lets the invalidation matrix work — one
 * page mutates, and every other consumer of the same key
 * automatically refreshes.
 *
 * Convention: use functions (not string constants) so keys can vary by
 * id (e.g. per-node) while still remaining stable references. Never
 * inline a key inline in a component — always call `qk.…()`.
 *
 * NOTE (RC1.3.2B Phase 1): We only need dashboard / mission / roadmap
 * keys for the components migrated in Phase 1. Weekly-activity and
 * analytics keys are declared here anyway so Phase 2 can pick them up
 * without a second refactor.
 */

export const qk = {
  // Dashboard payload (streak, readiness, mission-of-the-day summary,
  // revision count, knowledge progress, recent activity, week goal).
  // Read by: Topbar, MissionControl, CommandAnalytics.
  dashboard: () => ['dashboard'],

  // Today's mission — same underlying network call as `dashboard`
  // (server returns it nested). Kept as a distinct key ONLY when a
  // consumer specifically wants the mission sub-tree; use
  // `useDashboard()` for the general case.
  missionToday: () => ['dashboard', 'today'],

  // Weekly-activity roll-up (RC1.3 endpoint). Kept for Phase 2 wiring.
  weeklyActivity: () => ['dashboard', 'weekly-activity'],

  // Full roadmap tree with progress overlay (roadmapService.tree()).
  roadmapTree: () => ['roadmap', 'tree'],

  // Domain-level summary (roadmapService.summary()) — used by
  // MissionControl right rail.
  roadmapSummary: () => ['roadmap', 'summary'],

  // Deep node view (DeepTopicPage). Keyed by node id so multiple
  // nodes can be cached side-by-side (e.g. tab switching).
  roadmapNode: (nodeId) => ['roadmap', 'node', nodeId],
};

/**
 * Helper: given a node id, return every query key that could contain
 * that node's progress. Used by mutations that need to invalidate a
 * node from multiple angles (individual node + the aggregated tree).
 */
export function nodeAffectedKeys(nodeId) {
  return [
    qk.roadmapNode(nodeId),
    qk.roadmapTree(),
  ];
}
