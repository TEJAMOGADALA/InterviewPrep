import { Flag, AlertTriangle, Sparkles } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { useAIContent } from '@/hooks/useAIContent';

/**
 * Top-of-page summary cards — Interview Tips + Common Mistakes.
 * Renders nothing until AI content has been generated for this node.
 * Shares fetch state with <AIContentTabs> via the useAIContent hook cache,
 * so mounting both together triggers exactly ONE /content request.
 */
export function AIInterviewCards({ nodeId }) {
  const { content } = useAIContent(nodeId);
  if (!content?.available) return null;

  const tips = content.interview_tips || [];
  const mistakes = content.common_mistakes || [];
  if (tips.length === 0 && mistakes.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="ai-interview-cards">
      {tips.length > 0 && (
        <GlassCard className="p-5" data-testid="ai-top-tips">
          <div className="flex items-center gap-2 mb-3">
            <Flag className="h-4 w-4 text-primary" />
            <div className="overline text-primary">Interview Tips</div>
          </div>
          <ul className="space-y-2">
            {tips.map((t, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Sparkles className="h-3.5 w-3.5 text-primary mt-0.5 shrink-0" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      {mistakes.length > 0 && (
        <GlassCard className="p-5" data-testid="ai-top-mistakes">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="h-4 w-4 text-rose-300" />
            <div className="overline text-rose-300">Common Mistakes</div>
          </div>
          <ul className="space-y-2.5">
            {mistakes.map((m, i) => (
              <li key={i} className="text-sm">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-3.5 w-3.5 text-rose-300 mt-0.5 shrink-0" />
                  <span>{m.mistake}</span>
                </div>
                {m.fix && (
                  <div className="text-xs text-muted-foreground mt-1 pl-5">→ {m.fix}</div>
                )}
              </li>
            ))}
          </ul>
        </GlassCard>
      )}
    </div>
  );
}
