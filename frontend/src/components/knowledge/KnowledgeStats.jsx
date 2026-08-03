import { CheckCircle2, Bookmark, Star, TrendingDown, RefreshCw, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * KnowledgeStats (RC1.3.4)
 *
 * Compact stat strip rendered at the top of the Knowledge Base. Every
 * value is derived from data the caller already has in memory, so we
 * do NOT issue a second network round-trip — the summary payload
 * (`useRoadmapSummary`) is already shared with Mission Control and
 * the header.
 *
 * Semantic guarantee: the same numbers here match `/api/roadmap/summary`
 * exactly, which is the same source Mission Control's progress strip
 * reads. There is one source of truth per metric.
 */
function StatTile({ icon: Icon, label, value, hint, accent = 'primary', testId }) {
  const accentCls = {
    primary: 'text-primary bg-primary/10 border-primary/30',
    emerald: 'text-emerald-300 bg-emerald-400/10 border-emerald-400/30',
    amber:   'text-amber-300 bg-amber-400/10 border-amber-400/30',
    rose:    'text-rose-300 bg-rose-400/10 border-rose-400/30',
    sky:     'text-sky-300 bg-sky-400/10 border-sky-400/30',
  }[accent];
  return (
    <div
      data-testid={testId}
      className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3.5"
    >
      <div className="flex items-center gap-2 mb-1.5">
        <span className={cn('h-6 w-6 rounded-md border flex items-center justify-center', accentCls)}>
          <Icon className="h-3 w-3" />
        </span>
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground truncate">
          {label}
        </div>
      </div>
      <div className="font-display text-2xl font-semibold tracking-tight">{value}</div>
      {hint && <div className="text-[11px] text-muted-foreground mt-0.5 truncate">{hint}</div>}
    </div>
  );
}

export function KnowledgeStats({ summary, counts }) {
  // `summary` is the payload from `useRoadmapSummary()`. `counts` is
  // an object with client-side derived counts (weak, recent) that the
  // parent has already computed while building the view tabs.
  const overall = summary?.overall || {};
  const summaryCounts = summary?.counts || {};

  return (
    <div
      data-testid="kb-stats"
      className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3"
    >
      <StatTile
        icon={GraduationCap}
        label="Completed"
        value={`${overall.completed_topics ?? 0}/${overall.total_topics ?? 0}`}
        hint={`${Math.round(overall.completion_pct ?? 0)}% overall`}
        accent="emerald"
        testId="kb-stat-completed"
      />
      <StatTile
        icon={CheckCircle2}
        label="Readiness"
        value={`${Math.round(overall.readiness ?? 0)}%`}
        hint="weighted"
        accent="primary"
        testId="kb-stat-readiness"
      />
      <StatTile
        icon={Bookmark}
        label="Bookmarks"
        value={summaryCounts.bookmarked ?? 0}
        accent="primary"
        testId="kb-stat-bookmarks"
      />
      <StatTile
        icon={Star}
        label="Favorites"
        value={summaryCounts.favorite ?? 0}
        accent="amber"
        testId="kb-stat-favorites"
      />
      <StatTile
        icon={TrendingDown}
        label="Weak Topics"
        value={counts.weak ?? 0}
        hint="conf<4 or weakness≥50"
        accent="rose"
        testId="kb-stat-weak"
      />
      <StatTile
        icon={RefreshCw}
        label="Revision Due"
        value={summaryCounts.revision_due ?? 0}
        accent="amber"
        testId="kb-stat-revision"
      />
    </div>
  );
}
