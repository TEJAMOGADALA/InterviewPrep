import { cn } from '@/lib/utils';

// Normalized status vocabulary — matches backend routes_roadmap.py.
// `available` and `locked` are legacy aliases mapped to not_started.
const STATUS_LABEL = {
  not_started: 'Not Started',
  available: 'Not Started',
  locked: 'Not Started',
  in_progress: 'In Progress',
  completed: 'Completed',
  mastered: 'Mastered',
  revision_due: 'Revision Due',
};

const STATUS_STYLE = {
  not_started: 'text-muted-foreground bg-white/[0.03] border-white/[0.08]',
  available:   'text-muted-foreground bg-white/[0.03] border-white/[0.08]',
  locked:      'text-muted-foreground bg-white/[0.03] border-white/[0.06]',
  in_progress: 'text-primary bg-primary/10 border-primary/30',
  completed:   'text-emerald-300 bg-emerald-400/10 border-emerald-400/30',
  mastered:    'text-emerald-200 bg-emerald-400/20 border-emerald-400/40',
  revision_due:'text-amber-300 bg-amber-400/10 border-amber-400/30',
};

export function StatusBadge({ status, className }) {
  const key = STATUS_LABEL[status] ? status : 'not_started';
  return (
    <span
      data-testid={`status-badge-${key}`}
      className={cn(
        'inline-block text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full border',
        STATUS_STYLE[key],
        className,
      )}
    >
      {STATUS_LABEL[key]}
    </span>
  );
}

export const NORMALIZED_STATUSES = ['not_started', 'in_progress', 'completed', 'mastered', 'revision_due'];
