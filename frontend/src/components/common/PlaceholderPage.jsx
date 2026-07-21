import { GlassCard } from '@/components/common/GlassCard';
import { Sparkles } from 'lucide-react';

export function PlaceholderPage({ overline, title, description, icon: Icon = Sparkles, testId }) {
  return (
    <div data-testid={testId} className="space-y-6">
      <div>
        <div className="overline mb-2">{overline}</div>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">{description}</p>
      </div>

      <GlassCard className="p-10 flex flex-col items-center text-center">
        <span className="h-12 w-12 rounded-2xl bg-primary/15 border border-primary/30 flex items-center justify-center mb-4">
          <Icon className="h-5 w-5 text-primary" />
        </span>
        <h2 className="font-display text-xl font-medium mb-1.5">Shipping in a future drop</h2>
        <p className="text-sm text-muted-foreground max-w-md">
          This surface is architected and ready. The engine that powers it ships in the next phase.
          You'll find placeholder components here already wired into your workspace.
        </p>
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-2xl text-left">
          {['Foundation', 'Data model', 'UI shell'].map((s) => (
            <div key={s} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="overline mb-1">Ready</div>
              <p className="text-sm">{s}</p>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
