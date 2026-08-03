import { Layers, Bookmark, Star, TrendingDown, RefreshCw, History, PlayCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * KnowledgeViewTabs (RC1.3.4)
 *
 * Segmented control that swaps the Knowledge Base between its seven
 * workspace lenses. All lenses derive from the same in-memory tree
 * (`useRoadmapTree`) + a small revision-queue read + local recently-
 * viewed state — no additional network calls when switching.
 *
 * Each tab optionally displays a count badge; the parent computes the
 * counts from the same data it renders, so the badge and the list can
 * never drift apart.
 */
export const KNOWLEDGE_VIEWS = [
  { id: 'all',        label: 'All Topics',        icon: Layers,        testId: 'kb-view-all' },
  { id: 'continue',   label: 'Continue Learning', icon: PlayCircle,    testId: 'kb-view-continue' },
  { id: 'bookmarks',  label: 'Bookmarks',         icon: Bookmark,      testId: 'kb-view-bookmarks' },
  { id: 'favorites',  label: 'Favorites',         icon: Star,          testId: 'kb-view-favorites' },
  { id: 'weak',       label: 'Weak Topics',       icon: TrendingDown,  testId: 'kb-view-weak' },
  { id: 'revision',   label: 'Revision Due',      icon: RefreshCw,     testId: 'kb-view-revision' },
  { id: 'recent',     label: 'Recently Viewed',   icon: History,       testId: 'kb-view-recent' },
];

export function KnowledgeViewTabs({ active, onChange, counts = {} }) {
  return (
    <div
      role="tablist"
      data-testid="kb-view-tabs"
      className="flex flex-wrap gap-1.5 rounded-xl border border-white/[0.06] bg-white/[0.02] p-1.5"
    >
      {KNOWLEDGE_VIEWS.map(({ id, label, icon: Icon, testId }) => {
        const isActive = active === id;
        const count = counts[id];
        return (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={isActive}
            data-testid={testId}
            onClick={() => onChange(id)}
            className={cn(
              'inline-flex items-center gap-2 h-9 px-3 rounded-lg text-sm transition-colors',
              isActive
                ? 'bg-primary/15 border border-primary/40 text-primary'
                : 'border border-transparent text-muted-foreground hover:text-foreground hover:bg-white/[0.04]',
            )}
          >
            <Icon className="h-3.5 w-3.5 shrink-0" />
            <span className="whitespace-nowrap">{label}</span>
            {typeof count === 'number' && (
              <span
                className={cn(
                  'ml-1 min-w-[20px] h-5 inline-flex items-center justify-center rounded-full px-1.5 text-[11px] font-mono',
                  isActive
                    ? 'bg-primary/25 text-primary'
                    : 'bg-white/[0.05] text-muted-foreground',
                )}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
