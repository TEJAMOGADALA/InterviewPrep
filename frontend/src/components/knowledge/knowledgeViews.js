/**
 * knowledgeViews (RC1.3.4)
 *
 * Pure helpers that derive the seven Knowledge Base workspace views
 * from the same in-memory tree the current UI already renders. Every
 * function is a plain reducer over the tree — no network calls, no
 * hooks, no React — so consumers can memoise the results with cheap
 * dependencies and keep the workspace feeling instantaneous.
 *
 * Contract: `tree` is the payload returned by `useRoadmapTree()` /
 * `roadmapService.tree()`. Each leaf is a "topic" node carrying a
 * `progress` object with the same shape the backend already emits
 * (`bookmarked`, `favorite`, `confidence`, `weakness_score`,
 * `mastery_percentage`, `status`, `next_revision`, `updated_at`, …).
 *
 * A "leaf" for workspace purposes is any node with no children — this
 * matches how `_rollup_from_progress` in the backend distinguishes
 * atomic learning units from structural aggregates.
 */

const WEAK_CONFIDENCE = 4.0;
const WEAK_WEAKNESS = 50.0;

/**
 * Depth-first flatten to leaf topic nodes, tagging each with its
 * track for display purposes. Iterative to avoid the visual-edit
 * babel plugin call-stack issue KnowledgeBase.jsx already works
 * around.
 */
export function flattenLeaves(tree) {
  if (!tree || !Array.isArray(tree.tracks)) return [];
  const out = [];
  for (const track of tree.tracks) {
    const stack = [{ n: track, trackRef: { id: track.id, label: track.label } }];
    while (stack.length) {
      const { n, trackRef } = stack.pop();
      const kids = n.children || [];
      if (!kids.length) {
        // Skip the track itself as a "leaf" — only real topic leaves.
        if (n.id !== track.id) {
          out.push({ ...n, track: trackRef });
        }
        continue;
      }
      for (let i = kids.length - 1; i >= 0; i--) {
        stack.push({ n: kids[i], trackRef });
      }
    }
  }
  return out;
}

// Bookmark view — show all bookmarked leaves, alphabetical.
export function bookmarkView(leaves) {
  return leaves
    .filter((n) => n.progress?.bookmarked)
    .sort((a, b) => a.label.localeCompare(b.label));
}

export function favoriteView(leaves) {
  return leaves
    .filter((n) => n.progress?.favorite)
    .sort((a, b) => a.label.localeCompare(b.label));
}

/**
 * Weak-topics view.
 *
 * A leaf counts as weak when EITHER:
 *   • confidence < 4 (and non-zero — a completely untouched node with
 *     0 confidence is "unseen", not weak), OR
 *   • weakness_score ≥ 50, OR
 *   • status === "revision_due".
 *
 * Ranked by "weakness pressure":
 *   weakness_score - confidence*10 + (revision_due ? 20 : 0)
 * — bigger number = weaker. Matches the same signal the planner uses
 * (`_build_support_recommendation` in planner.py). We deliberately
 * do NOT reinvent a weakness algorithm.
 */
export function weakView(leaves) {
  const weaknessScore = (n) => {
    const p = n.progress || {};
    return (p.weakness_score || 0)
      - (p.confidence || 0) * 10
      + (p.status === 'revision_due' ? 20 : 0);
  };
  return leaves
    .filter((n) => {
      const p = n.progress || {};
      const conf = p.confidence || 0;
      const weakness = p.weakness_score || 0;
      const attempted = (p.attempts || 0) > 0 || p.status !== 'not_started';
      return attempted && (
        (conf > 0 && conf < WEAK_CONFIDENCE)
        || weakness >= WEAK_WEAKNESS
        || p.status === 'revision_due'
      );
    })
    .map((n) => ({
      ...n,
      meta: `weakness ${Math.round(n.progress.weakness_score || 0)} · conf ${(n.progress.confidence || 0).toFixed(1)}`,
      metaAccent: 'rose',
    }))
    .sort((a, b) => weaknessScore(b) - weaknessScore(a));
}

/**
 * Continue Learning view.
 *
 * Union of:
 *   • every leaf whose status is exactly "in_progress"
 *   • the most-recently-viewed leaves (from useRecentlyViewed) that
 *     are NOT completed/mastered
 *
 * Deduped by node id, ranked so the last-opened topic comes first
 * (viewedAt), followed by attempts-based recency for in-progress
 * leaves the learner has never actually opened on this device.
 */
export function continueLearningView(leaves, recentEntries) {
  const recentIndex = new Map(recentEntries.map((e, i) => [e.nodeId, i]));
  const now = Date.now();
  const rows = [];
  const seen = new Set();

  for (const n of leaves) {
    const p = n.progress || {};
    const inProgress = p.status === 'in_progress';
    const recent = recentIndex.has(n.id) && p.status !== 'completed' && p.status !== 'mastered';
    if (!inProgress && !recent) continue;
    if (seen.has(n.id)) continue;
    seen.add(n.id);

    const openedAt = recent ? recentEntries[recentIndex.get(n.id)]?.viewedAt : null;
    rows.push({
      ...n,
      _openedAt: openedAt ? new Date(openedAt).getTime() : 0,
      _updatedAt: p.updated_at ? new Date(p.updated_at).getTime() : 0,
      meta: openedAt
        ? relativeTimeMeta(openedAt, 'opened')
        : (p.status === 'in_progress' ? 'in progress' : null),
      metaAccent: 'emerald',
    });
  }

  rows.sort((a, b) => {
    // Newest touch first — either opened or updated.
    const aT = Math.max(a._openedAt, a._updatedAt);
    const bT = Math.max(b._openedAt, b._updatedAt);
    if (bT !== aT) return bT - aT;
    // Then higher unfinished progress (closer to done first).
    const aP = a.progress?.mastery_percentage || 0;
    const bP = b.progress?.mastery_percentage || 0;
    return bP - aP;
  });

  // Strip helper fields before rendering.
  return rows.map(({ _openedAt: _oa, _updatedAt: _ua, ...rest }) => rest);
}

/**
 * Recently Viewed view — direct projection of the local hook, joined
 * against the tree to hydrate `label` / `track` / `progress`. Nodes
 * removed from the roadmap (rare) are silently skipped.
 */
export function recentlyViewedView(leaves, recentEntries) {
  const byId = new Map(leaves.map((n) => [n.id, n]));
  return recentEntries
    .map((entry) => {
      const node = byId.get(entry.nodeId);
      if (!node) return null;
      return {
        ...node,
        meta: relativeTimeMeta(entry.viewedAt, 'opened'),
        metaAccent: 'emerald',
      };
    })
    .filter(Boolean);
}

/**
 * Revision Due view — grouped by bucket:
 *   overdue  · next_review_date < today
 *   today    · next_review_date === today
 *   tomorrow · next_review_date === today+1
 *   upcoming · next_review_date > today+1
 *
 * Uses the canonical `/api/revisions/queue` payload — same source
 * the Mission Control widget reads — so cards and the widget can
 * never disagree.
 */
export function revisionDueGroups(revisionRows, leaves) {
  const byId = new Map(leaves.map((n) => [n.id, n]));
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today.getTime() + 86_400_000);

  const groups = {
    overdue:  { id: 'overdue',  label: 'Overdue',  rows: [] },
    today:    { id: 'today',    label: 'Today',    rows: [] },
    tomorrow: { id: 'tomorrow', label: 'Tomorrow', rows: [] },
    upcoming: { id: 'upcoming', label: 'Upcoming', rows: [] },
  };

  for (const r of revisionRows || []) {
    const dueRaw = r.next_review_date;
    if (!dueRaw) continue;
    const due = new Date(dueRaw);
    if (Number.isNaN(due.getTime())) continue;
    due.setHours(0, 0, 0, 0);
    const node = byId.get(r.node_id) || { id: r.node_id, label: r.task_title, progress: {} };
    const row = {
      ...node,
      meta: r.is_due
        ? relativeTimeMeta(dueRaw, 'due')
        : `Due ${dueFromNow(due, today)}`,
      metaAccent: r.is_due ? 'rose' : (due.getTime() === today.getTime() ? 'amber' : 'emerald'),
    };
    if (due < today) groups.overdue.rows.push(row);
    else if (due.getTime() === today.getTime()) groups.today.rows.push(row);
    else if (due.getTime() === tomorrow.getTime()) groups.tomorrow.rows.push(row);
    else groups.upcoming.rows.push(row);
  }
  return [groups.overdue, groups.today, groups.tomorrow, groups.upcoming];
}

/**
 * The canonical "row → passes the current search+filter" predicate.
 * We reuse the existing `matchNode` predicate (used by the tree view)
 * so filter chips behave identically across every workspace view —
 * no second predicate to keep in sync.
 */
export function filterRows(rows, query, filters, matchNode) {
  const needle = (query || '').trim().toLowerCase();
  const hasFilters = filters && filters.size > 0;
  if (!needle && !hasFilters) return rows;
  return rows.filter((r) => {
    if (needle) {
      const label = (r.label || '').toLowerCase();
      const id = (r.id || '').toLowerCase();
      if (!label.includes(needle) && !id.includes(needle)) return false;
    }
    if (hasFilters && !matchNode(r, filters)) return false;
    return true;
  });
}

// ---------- Internals -------------------------------------------------

function dueFromNow(due, today) {
  const days = Math.round((due.getTime() - today.getTime()) / 86_400_000);
  if (days === 1) return 'tomorrow';
  return `in ${days} days`;
}

function relativeTimeMeta(iso, label) {
  const diffMs = Date.now() - new Date(iso).getTime();
  if (!Number.isFinite(diffMs)) return null;
  const abs = Math.abs(diffMs);
  const past = diffMs > 0;
  const suffix = past ? 'ago' : 'from now';
  if (abs < 60_000) return `${label} just now`;
  if (abs < 3_600_000) return `${label} ${Math.round(abs / 60_000)}m ${suffix}`;
  if (abs < 86_400_000) return `${label} ${Math.round(abs / 3_600_000)}h ${suffix}`;
  return `${label} ${Math.round(abs / 86_400_000)}d ${suffix}`;
}
