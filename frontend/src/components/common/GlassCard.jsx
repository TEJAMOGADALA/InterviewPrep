import { cn } from '@/lib/utils';

export function GlassCard({ className, children, as: Comp = 'div', ...rest }) {
  return (
    <Comp
      className={cn(
        'rounded-2xl border border-white/[0.08] bg-[hsl(var(--surface))]/70 backdrop-blur-xl',
        'shadow-[0_1px_0_0_rgba(255,255,255,0.04)_inset]',
        className,
      )}
      {...rest}
    >
      {children}
    </Comp>
  );
}
