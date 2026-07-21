import { cn } from '@/lib/utils';

/**
 * Slim, theme-matched progress bar. Accepts a `value` 0-100.
 * Colors match the app palette; a subtle glow at 100%.
 */
export function ProgressBar({ value = 0, className, showValue = false, size = 'md' }) {
  const pct = Math.max(0, Math.min(100, Number(value) || 0));
  const barH = size === 'sm' ? 'h-1' : size === 'lg' ? 'h-2.5' : 'h-1.5';
  return (
    <div className={cn('flex items-center gap-2', className)} data-testid="progress-bar">
      <div className={cn('flex-1 rounded-full bg-white/[0.05] overflow-hidden', barH)}>
        <div
          className={cn(
            'h-full transition-[width] duration-500 ease-out',
            pct >= 100 ? 'bg-emerald-400 shadow-[0_0_12px_-2px_rgba(52,211,153,0.6)]' : 'bg-primary',
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showValue && (
        <span className="font-mono text-[11px] text-muted-foreground w-10 text-right">
          {Math.round(pct)}%
        </span>
      )}
    </div>
  );
}
