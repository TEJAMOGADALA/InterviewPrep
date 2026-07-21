import { useState } from 'react';
import { Bookmark, Star } from 'lucide-react';
import { toast } from 'sonner';
import { roadmapService } from '@/services/mission.service';
import { cn } from '@/lib/utils';

/**
 * Bookmark ("save for later") + Favorite ("star for quick access") toggles.
 * Optimistic: state flips instantly and rolls back on error.
 *
 * onChange(node_id, { bookmarked, favorite }) fires so parent caches can
 * refresh derived counts without a full refetch.
 */
export function NodeActions({ nodeId, bookmarked = false, favorite = false, onChange }) {
  const [bm, setBm] = useState(!!bookmarked);
  const [fav, setFav] = useState(!!favorite);
  const [pending, setPending] = useState(false);

  const toggle = async (kind) => {
    if (pending) return;
    setPending(true);
    const prev = kind === 'bookmark' ? bm : fav;
    // Optimistic flip.
    if (kind === 'bookmark') setBm(!prev);
    else setFav(!prev);
    try {
      const res = kind === 'bookmark'
        ? await roadmapService.toggleBookmark(nodeId)
        : await roadmapService.toggleFavorite(nodeId);
      const next = kind === 'bookmark' ? res.bookmarked : res.favorite;
      if (kind === 'bookmark') setBm(next);
      else setFav(next);
      onChange?.(nodeId, { bookmarked: kind === 'bookmark' ? next : bm, favorite: kind === 'favorite' ? next : fav });
    } catch (e) {
      if (kind === 'bookmark') setBm(prev);
      else setFav(prev);
      toast.error(`Could not update ${kind}`);
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="inline-flex items-center gap-1" data-testid={`node-actions-${nodeId}`}>
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); e.preventDefault(); toggle('bookmark'); }}
        aria-pressed={bm}
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
