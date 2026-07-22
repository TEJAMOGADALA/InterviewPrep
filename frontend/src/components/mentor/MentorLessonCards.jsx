import { motion } from 'framer-motion';
import {
  Sparkles, Code2, Layers, Zap, TrendingUp, Building2,
  AlertTriangle, ListChecks, Route, ArrowRight, BookOpen,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { GlassCard } from '@/components/common/GlassCard';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

/**
 * MentorLessonCards — renders the 9-card structured lesson response.
 *
 * The mentor emits JSON matching the schema in mentor_prompt.LESSON_JSON_SCHEMA_HINT.
 * We render each section as a distinct card with its own icon + accent color
 * so the reader can scan the lesson like a Notion page rather than parsing a
 * wall of markdown.
 */

const CARDS = [
  {
    key: 'executive_summary', title: 'Executive Summary',
    icon: Sparkles, accent: 'text-primary bg-primary/12 border-primary/25',
  },
  {
    key: 'core_concept', title: 'Core Concept',
    icon: BookOpen, accent: 'text-emerald-300 bg-emerald-400/10 border-emerald-400/25',
  },
  {
    key: 'internal_working', title: 'Internal Working',
    icon: Layers, accent: 'text-sky-300 bg-sky-400/10 border-sky-400/25',
  },
  {
    key: 'implementation', title: 'Java Implementation',
    icon: Code2, accent: 'text-amber-300 bg-amber-400/10 border-amber-400/25',
  },
  {
    key: 'complexity', title: 'Complexity',
    icon: Zap, accent: 'text-fuchsia-300 bg-fuchsia-400/10 border-fuchsia-400/25',
  },
  {
    key: 'interview_insights', title: 'Interview Insights',
    icon: Building2, accent: 'text-indigo-300 bg-indigo-400/10 border-indigo-400/25',
  },
  {
    key: 'common_mistakes', title: 'Common Mistakes',
    icon: AlertTriangle, accent: 'text-rose-300 bg-rose-400/10 border-rose-400/25',
  },
  {
    key: 'practice_plan', title: 'Practice Plan',
    icon: ListChecks, accent: 'text-teal-300 bg-teal-400/10 border-teal-400/25',
  },
  {
    key: 'next_learning_path', title: 'Next Learning Path',
    icon: Route, accent: 'text-primary bg-primary/12 border-primary/25',
  },
];

function CardHeader({ icon: Icon, title, accent }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <span className={cn('h-8 w-8 rounded-lg border flex items-center justify-center', accent)}>
        <Icon className="h-4 w-4" />
      </span>
      <h3 className="font-display text-base font-semibold tracking-tight">{title}</h3>
    </div>
  );
}

function CardShell({ children, index, meta }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.03 }}
    >
      <GlassCard className="p-5">
        <CardHeader icon={meta.icon} title={meta.title} accent={meta.accent} />
        <div className="space-y-2.5 text-sm text-foreground/90">{children}</div>
      </GlassCard>
    </motion.div>
  );
}

// ---------- Section renderers ----------

function ExecutiveSummary({ data }) {
  if (!data) return null;
  return (
    <>
      {data.why_it_matters && (<p><span className="text-primary/90 font-medium">Why it matters · </span>{data.why_it_matters}</p>)}
      {data.target_company_relevance && (<p><span className="text-primary/90 font-medium">Target companies · </span>{data.target_company_relevance}</p>)}
      {data.why_next && (<p><span className="text-primary/90 font-medium">Why this is next · </span>{data.why_next}</p>)}
    </>
  );
}

function CoreConcept({ data }) {
  if (!data) return null;
  return (
    <>
      {data.definition && (<p className="italic text-foreground">{data.definition}</p>)}
      {data.explanation && (<p>{data.explanation}</p>)}
      {data.visualization && (
        <pre className="mt-2 rounded-lg border border-white/10 bg-black/40 p-3 text-xs whitespace-pre-wrap font-mono text-foreground/80">
{data.visualization}
        </pre>
      )}
    </>
  );
}

function InternalWorking({ data }) {
  if (!data) return null;
  return (
    <>
      {data.flow && (<div><div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Flow</div><p>{data.flow}</p></div>)}
      {data.architecture && (<div><div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Architecture</div><p>{data.architecture}</p></div>)}
    </>
  );
}

function Implementation({ data }) {
  if (!data) return null;
  return (
    <>
      <div className="text-xs text-muted-foreground uppercase tracking-wider">{data.language || 'Java'}</div>
      {data.code && (
        <pre className="rounded-lg border border-white/10 bg-black/50 p-3 overflow-x-auto text-xs font-mono text-foreground/90">
<code>{data.code}</code>
        </pre>
      )}
      {data.explanation && (<p className="text-muted-foreground">{data.explanation}</p>)}
    </>
  );
}

function Complexity({ data }) {
  if (!data) return null;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1">Time</div>
        <div className="text-sm">{data.time || '—'}</div>
      </div>
      <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1">Space</div>
        <div className="text-sm">{data.space || '—'}</div>
      </div>
      <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1">Tradeoffs</div>
        <div className="text-sm">{data.tradeoffs || '—'}</div>
      </div>
    </div>
  );
}

function InterviewInsights({ data }) {
  if (!data) return null;
  return (
    <>
      {Array.isArray(data.companies) && data.companies.length > 0 && (
        <div className="space-y-2">
          {data.companies.map((c, i) => (
            <div key={i} className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
              <div className="text-xs font-mono uppercase tracking-wider text-primary/80">{c.name}</div>
              <div className="text-sm mt-1">{c.signal}</div>
            </div>
          ))}
        </div>
      )}
      {Array.isArray(data.common_questions) && data.common_questions.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Common questions</div>
          <ul className="list-disc list-inside space-y-1">
            {data.common_questions.map((q, i) => (<li key={i}>{q}</li>))}
          </ul>
        </div>
      )}
    </>
  );
}

function CommonMistakes({ data }) {
  if (!data) return null;
  return (
    <>
      {Array.isArray(data.mistakes) && data.mistakes.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Mistakes</div>
          <ul className="list-disc list-inside space-y-1">
            {data.mistakes.map((m, i) => (<li key={i}>{m}</li>))}
          </ul>
        </div>
      )}
      {Array.isArray(data.edge_cases) && data.edge_cases.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Edge cases</div>
          <ul className="list-disc list-inside space-y-1">
            {data.edge_cases.map((e, i) => (<li key={i}>{e}</li>))}
          </ul>
        </div>
      )}
    </>
  );
}

function PracticePlan({ data }) {
  if (!data) return null;
  const bucket = (label, items, color) => (
    <div>
      <div className="flex items-center gap-2 mb-1.5">
        <Badge variant="outline" className={cn('text-[10px] font-mono py-0 px-2', color)}>{label}</Badge>
      </div>
      <ul className="space-y-1.5">
        {(items || []).map((p, i) => (
          <li key={i} className="rounded-md border border-white/[0.06] bg-white/[0.02] px-2.5 py-1.5">
            <div className="text-sm font-medium">{p.title}</div>
            {p.why && <div className="text-xs text-muted-foreground mt-0.5">{p.why}</div>}
          </li>
        ))}
      </ul>
    </div>
  );
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      {bucket('Easy', data.easy, 'text-emerald-300 border-emerald-400/30')}
      {bucket('Medium', data.medium, 'text-amber-300 border-amber-400/30')}
      {bucket('Hard', data.hard, 'text-rose-300 border-rose-400/30')}
    </div>
  );
}

function NextLearningPath({ data }) {
  if (!data) return null;
  const next = data.next_topic;
  return (
    <>
      {next && (
        <div className="rounded-lg border border-primary/30 bg-primary/[0.08] p-3">
          <div className="text-xs font-mono uppercase tracking-wider text-primary/80 mb-1">Next topic</div>
          <div className="flex items-center gap-2">
            <div className="text-base font-medium">{next.label}</div>
            {next.node_id && (
              <Link
                to={`/app/knowledge-base/nodes/${next.node_id}`}
                className="text-xs text-primary hover:text-primary/80 inline-flex items-center gap-1"
              >
                Open <ArrowRight className="h-3 w-3" />
              </Link>
            )}
          </div>
        </div>
      )}
      {data.reason && <p><span className="text-primary/90 font-medium">Why · </span>{data.reason}</p>}
      {Array.isArray(data.sequence) && data.sequence.length > 0 && (
        <div className="mt-2">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5">Sequence</div>
          <div className="flex flex-wrap gap-1.5">
            {data.sequence.map((t, i) => (
              <span key={i} className="flex items-center gap-1 text-xs">
                <span className="px-2 py-0.5 rounded-md border border-white/10 bg-white/[0.02]">{t}</span>
                {i < data.sequence.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground" />}
              </span>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

const RENDERERS = {
  executive_summary: ExecutiveSummary,
  core_concept: CoreConcept,
  internal_working: InternalWorking,
  implementation: Implementation,
  complexity: Complexity,
  interview_insights: InterviewInsights,
  common_mistakes: CommonMistakes,
  practice_plan: PracticePlan,
  next_learning_path: NextLearningPath,
};

export function MentorLessonCards({ lesson, testId }) {
  if (!lesson || typeof lesson !== 'object') return null;
  return (
    <div data-testid={testId} className="grid grid-cols-1 gap-3">
      {CARDS.map((meta, i) => {
        const data = lesson[meta.key];
        const Renderer = RENDERERS[meta.key];
        if (!data || !Renderer) return null;
        return (
          <CardShell key={meta.key} index={i} meta={meta}>
            <Renderer data={data} />
          </CardShell>
        );
      })}
    </div>
  );
}

export default MentorLessonCards;
