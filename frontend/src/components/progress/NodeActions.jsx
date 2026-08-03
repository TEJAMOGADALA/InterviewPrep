import { Bookmark, Star } from 'lucide-react';
import { useToggleBookmark, useToggleFavorite } from '@/queries/mutations';
import { cn } from '@/lib/utils';

/**
 * Bookmark ("save for later") + Favorite ("star for quick access") toggles.
 *
 * RC1.3.3 · Migrated to the React Query mutation hooks introduced in
 * RC1.3.2B (`useToggleBookmark` / `useToggleFavorite`). This gives us
 * three properties for free:
 *
 *   1. Optimistic UI — the mutation flips `progress.bookmarked` /
 *      `progress.favorite` in BOTH the deep-node cache and the
 *      matching leaf of the roadmap tree cache before the network
 *      round-trip. No local `useState` mirror needed.
 *   2. Automatic rollback on failure — the mutation restores the
 *      snapshot and surfaces a toast, so we no longer need to track
 *      `prev` ourselves.
 *   3. Cache invalidation — every consumer of the deep-node cache
 *      re-renders with the new value automatically. This is what
 *      the old `onChange` callback (whose target `load` was removed
 *      during the migration) used to do imperatively; React Query
 *      now handles it declaratively.
 *
 * `bookmarked` / `favorite` come straight from the parent's cached
 * roadmap-node payload, so they always reflect the optimistic (or
 * server-confirmed) state without a second source of truth. The
 * `onChange` prop is preserved for backwards-compatibility but is
 * now optional — legacy callers that supplied one will still be
 * notified; new callers can omit it entirely.
 */
export function NodeActions({ nodeId, bookmarked = false, favorite = false, onChange }) {
  const toggleBookmarkM = useToggleBookmark();
  const toggleFavoriteM = useToggleFavorite();
  const bm = !!bookmarked;
  const fav = !!favorite;
  const pending = toggleBookmarkM.isPending || toggleFavoriteM.isPending;

  const toggle = (kind) => {
    if (pending) return;
    const mutation = kind === 'bookmark' ? toggleBookmarkM : toggleFavoriteM;
    mutation.mutate(nodeId, {
      onSuccess: (res) => {
        // Preserve the legacy `onChange` contract so any parent still
        // wiring it in (there are none left in tree, but the signature
        // is safe to keep for external consumers) receives the
        // server-confirmed values.
        onChange?.(nodeId, {
          bookmarked: kind === 'bookmark' ? !!res?.bookmarked : bm,
          favorite:   kind === 'favorite' ? !!res?.favorite   : fav,
        });
      },
    });
  };

  return (
    <div className="inline-flex items-center gap-1" data-testid={`node-actions-${nodeId}`}>
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); e.preventDefault(); toggle('bookmark'); }}
        aria-pressed={bm}
        disabled={pending}
        title={bm ? 'Remove bookmark' : 'Bookmark for later'}
        data-testid={`node-bookmark-${nodeId}`}
        className={cn(
          'h-7 w-7 inline-flex items-center justify-center rounded-md border transition-colors',
          bm
            ? 'text-primary bg-primary/10 border-primary/30'
            : 'text-muted-foreground bg-white/[0.02] border-white/[0.06] hover:text-primary hover:border-primary/30',
        )}
      >
        <Bookmark className={cn('h-3.5 w-3.5', bm && 'fill-current')} />
      </button>
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); e.preventDefault(); toggle('favorite'); }}
        aria-pressed={fav}
        disabled={pending}
        title={fav ? 'Unfavorite' : 'Star for quick access'}
        data-testid={`node-favorite-${nodeId}`}
        className={cn(
          'h-7 w-7 inline-flex items-center justify-center rounded-md border transition-colors',
          fav
            ? 'text-amber-300 bg-amber-400/10 border-amber-400/30'
            : 'text-muted-foreground bg-white/[0.02] border-white/[0.06] hover:text-amber-300 hover:border-amber-400/30',
        )}
      >
        <Star className={cn('h-3.5 w-3.5', fav && 'fill-current')} />
      </button>
    </div>
  );
}
