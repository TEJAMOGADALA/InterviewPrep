import { CheckCircle2, Circle, Clock } from 'lucide-react';
import { ProgressBar } from './ProgressBar';

/**
 * Category stats card — shows completed / remaining / % / hours remaining.
 * Composable; works for a Track, Module or Topic node.
 *
 * Expects a `progress` object shaped like the backend rollup:
 *   { completion_pct, completed_topics, total_topics, remaining_topics,
 *     estimated_hours_remaining, mastery_percentage }
 */
export function CategoryStats({ progress, className = '', compact = false }) {
  const p = progress || {};
  const pct = p.completion_pct ?? p.mastery_percentage ?? 0;
  const done = p.completed_topics ?? 0;
  const total = p.total_topics ?? 0;
  const remaining = p.remaining_topics ?? Math.max(0, total - done);
  const hours = p.estimated_hours_remaining ?? 0;

  if (compact) {
    return (
      <div className={`flex items-center gap-3 text-xs text-muted-foreground ${className}`}
           data-testid="category-stats-compact">
        <span className="font-mono">{done}/{total}</span>
        <ProgressBar value={pct} className="w-24" size="sm" />
        <span className="font-mono">{Math.round(pct)}%</span>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`} data-testid="category-stats">
      <ProgressBar value={pct} showValue />
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1.5" data-testid="category-stats-completed">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-mono">{done}</span>
          <span>completed</span>
        </span>
        <span className="inline-flex items-center gap-1.5" data-testid="category-stats-remaining">
          <Circle className="h-3.5 w-3.5" />
          <span className="font-mono">{remaining}</span>
          <span>remaining</span>
        </span>
        <span className="inline-flex items-center gap-1.5" data-testid="category-stats-hours">
          <Clock className="h-3.5 w-3.5" />
          <span className="font-mono">{hours}</span>
          <span>h left</span>
        </span>
      </div>
    </div>
  );
}
