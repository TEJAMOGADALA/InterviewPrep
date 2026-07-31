import { Info, Building2, TrendingDown, Target, Clock, Sparkles, Zap, ShieldCheck, Route, ArrowRight, Waypoints } from 'lucide-react';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { TARGET_COMPANIES } from '@/config/companies';
import { cn } from '@/lib/utils';
import { DASHBOARD } from '@/constants/testIds';

/**
 * WhyThisMissionDialog (RC1.3)
 *
 * Replaces the always-visible "Why this mission" block inside Today's Mission
 * with a compact button that opens a premium dialog. All fields come from the
 * `recommendation_insight` object produced by the Learning Engine — nothing
 * is derived here, we only render.
 */
function StatCard({ icon: Icon, label, value, hint, accent = 'primary' }) {
  const accentCls = {
    primary: 'text-primary bg-primary/10 border-primary/25',
    emerald: 'text-emerald-300 bg-emerald-400/10 border-emerald-400/25',
    amber:   'text-amber-300 bg-amber-400/10 border-amber-400/25',
    rose:    'text-rose-300 bg-rose-400/10 border-rose-400/25',
    sky:     'text-sky-300 bg-sky-400/10 border-sky-400/25',
  }[accent];
  return (
    <div className="rounded-lg border hairline bg-foreground/[0.02] p-3">
      <div className="flex items-center gap-2 mb-1.5">
        <span className={cn('h-6 w-6 rounded-md border flex items-center justify-center', accentCls)}>
          <Icon className="h-3 w-3" />
        </span>
        <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">{label}</div>
      </div>
      <div className="text-lg font-display font-semibold tracking-tight">{value}</div>
      {hint && <div className="text-[11px] text-muted-foreground mt-0.5">{hint}</div>}
    </div>
  );
}

function formatCompanyName(id) {
  const c = TARGET_COMPANIES.find((x) => x.id === id);
  return c?.name || id.replace('_', ' ').replace(/\b\w/g, (m) => m.toUpperCase());
}

export function WhyThisMissionDialog({ insight, missionTitle, focusArea }) {
  if (!insight) return null;

  const confidence = typeof insight.confidence === 'number' ? insight.confidence : null;
  const weakness = typeof insight.weakness === 'number' ? insight.weakness : null;
  const mastery = typeof insight.mastery === 'number' ? insight.mastery : null;
  const freq = typeof insight.interview_frequency === 'number' ? insight.interview_frequency : null;
  const overall = insight.overall_score;
  const pacing = insight.pacing || {};
  const company = insight.company_relevance || {};
  const perCompany = company.per_company || {};
  const topCompany = company.top_company;
  const fits = insight.fits_today_study_time;
  const estMin = insight.estimated_study_minutes;
  const highlights = insight.highlights || [];
  const explanation = insight.explanation || '';

  const sortedCompanies = Object.entries(perCompany)
    .sort((a, b) => (b[1] || 0) - (a[1] || 0));

  // RC1.3.2A · additive planner signals — render only when the backend
  // populates them so this component stays backwards-compatible.
  const composition = insight.composition;
  const continuity = insight.continuity;
  const likelyNext = Array.isArray(insight.likely_next_topics) ? insight.likely_next_topics : [];
  const readiness = insight.readiness_delta_estimate;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          data-testid={DASHBOARD.whyThisMissionButton}
          className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded-full border border-primary/30 bg-primary/10 hover:bg-primary/15 text-[11px] font-medium text-primary transition-colors"
        >
          <Info className="h-3 w-3" />
          Why this?
        </button>
      </DialogTrigger>
      <DialogContent
        data-testid={DASHBOARD.whyThisMissionDialog}
        className="max-w-2xl max-h-[85vh] overflow-y-auto bg-[hsl(var(--surface))]/95 backdrop-blur-xl"
      >
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <span className="h-7 w-7 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
            </span>
            <span className="text-[10px] font-mono uppercase tracking-wider text-primary/80">
              Adaptive explanation
            </span>
          </div>
          <DialogTitle className="font-display text-xl tracking-tight">
            {missionTitle || 'Why this mission?'}
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            {focusArea ? <>Focus · <span className="text-foreground/80">{focusArea}</span> · </> : null}
            Derived from your progress signals — the same ones the ranking engine used.
          </DialogDescription>
        </DialogHeader>

        {/* Signal grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-2">
          <StatCard icon={Target} label="Ranking score" value={overall != null ? overall.toFixed(2) : '—'} accent="primary" />
          <StatCard icon={ShieldCheck} label="Confidence" value={confidence != null ? `${confidence.toFixed(1)}/10` : '—'} accent={confidence != null && confidence <= 4 ? 'rose' : 'emerald'} />
          <StatCard icon={TrendingDown} label="Weakness" value={weakness != null ? `${Math.round(weakness)}` : '—'} accent={weakness != null && weakness >= 50 ? 'rose' : 'sky'} />
          <StatCard icon={Zap} label="Mastery" value={mastery != null ? `${Math.round(mastery)}%` : '—'} accent="primary" />
          <StatCard icon={Building2} label="Company relevance" value={topCompany ? formatCompanyName(topCompany) : '—'} hint={company.score ? `${company.score.toFixed(1)} weighted` : ''} accent="sky" />
          <StatCard icon={Clock} label="Interview freq." value={freq != null ? `${freq.toFixed(1)}/5` : '—'} accent={freq != null && freq >= 4 ? 'amber' : 'sky'} />
          <StatCard
            icon={Route}
            label="Urgency"
            value={pacing.mode ? String(pacing.mode).replace('_', ' ') : '—'}
            hint={pacing.remaining_days != null ? `${pacing.remaining_days} days to target` : ''}
            accent={pacing.urgency && pacing.urgency > 1.5 ? 'rose' : 'primary'}
          />
          <StatCard
            icon={Clock}
            label="Study window"
            value={estMin ? `${estMin} min` : '—'}
            hint={fits === true ? 'Fits today' : fits === false ? "Longer than today's window" : ''}
            accent={fits === false ? 'amber' : 'emerald'}
          />
        </div>

        {/* Per-company breakdown */}
        {sortedCompanies.length > 0 && (
          <div className="mt-4 rounded-lg border hairline bg-foreground/[0.02] p-4">
            <div className="overline mb-2 flex items-center gap-2">
              <Building2 className="h-3.5 w-3.5 text-primary" />
              Company importance
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-3 gap-y-1.5">
              {sortedCompanies.slice(0, 9).map(([cid, val]) => {
                const stars = Math.max(0, Math.min(5, Math.round(val || 0)));
                return (
                  <div key={cid} className="flex items-center justify-between text-xs">
                    <span className="truncate">{formatCompanyName(cid)}</span>
                    <span className="text-amber-400 font-mono tracking-wider text-[13px] leading-none">
                      {'★'.repeat(stars) + '☆'.repeat(5 - stars)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Explanation */}
        {explanation && (
          <div className="mt-4 rounded-lg border border-primary/25 bg-primary/[0.05] px-4 py-3">
            <div className="overline text-primary mb-2">Adaptive reasoning</div>
            <div className="text-sm whitespace-pre-line text-foreground/95 leading-relaxed">
              {explanation}
            </div>
          </div>
        )}

        {/* Highlights */}
        {highlights.length > 0 && (
          <div className="mt-4">
            <div className="overline mb-2">Supporting signals</div>
            <div className="flex flex-wrap gap-1.5">
              {highlights.map((h, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className="text-[11px] border-primary/30 bg-primary/[0.08] text-primary/90"
                >
                  {h}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* RC1.3.2A · Likely Next Topics.
            Deliberately named "Likely" (not "Future Unlocks") because future
            missions remain adaptive — this is a preview, not a guarantee. */}
        {likelyNext.length > 0 && (
          <div className="mt-4 rounded-lg border hairline bg-foreground/[0.02] p-4">
            <div className="overline mb-2 flex items-center gap-2">
              <Waypoints className="h-3.5 w-3.5 text-primary" />
              Likely next topics
              <span className="text-[10px] font-mono normal-case tracking-normal text-muted-foreground/80 ml-1">
                · planner preview, not guaranteed
              </span>
            </div>
            <div className="space-y-1.5">
              {likelyNext.map((t, i) => (
                <div key={t.node_id || i} className="flex items-center gap-2 text-sm">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-primary/10 border border-primary/25 text-primary/90 shrink-0">
                    {t.when || 'next'}
                  </span>
                  <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />
                  <span className="flex-1 min-w-0 truncate text-foreground/95">{t.label}</span>
                  {t.why && (
                    <span className="hidden sm:inline text-[11px] text-muted-foreground truncate max-w-[45%]">
                      {t.why}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RC1.3.2A · Company Readiness — planner ESTIMATE, clearly labelled. */}
        {readiness && Object.keys(readiness.delta || {}).length > 0 && (
          <div className="mt-4 rounded-lg border hairline bg-foreground/[0.02] p-4">
            <div className="overline mb-1 flex items-center gap-2">
              <Building2 className="h-3.5 w-3.5 text-primary" />
              Projected readiness gain
              <span className="text-[10px] font-mono normal-case tracking-normal text-amber-300 ml-1">
                · {readiness.label || 'planner estimate'}
              </span>
            </div>
            <div className="text-[11px] text-muted-foreground mb-2">
              These are model-based estimates, not guarantees — the actual gain depends on how well the topic sticks.
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-3 gap-y-1.5">
              {Object.entries(readiness.delta).map(([cid, delta]) => {
                const before = (readiness.before || {})[cid];
                const after = (readiness.after || {})[cid];
                const sign = delta >= 0 ? '+' : '';
                return (
                  <div key={cid} className="flex items-center justify-between text-xs">
                    <span className="truncate capitalize">{cid.replace('_', ' ')}</span>
                    <span className="flex items-center gap-1 shrink-0">
                      <span className="text-muted-foreground font-mono text-[10px]">
                        {before != null ? `${before.toFixed(1)}→${after != null ? after.toFixed(1) : '—'}` : ''}
                      </span>
                      <span className={cn(
                        'font-mono text-xs',
                        delta > 0 ? 'text-emerald-300' : delta < 0 ? 'text-rose-300' : 'text-muted-foreground',
                      )}>
                        {sign}{Number(delta).toFixed(1)} pp
                      </span>
                    </span>
                  </div>
                );
              })}
            </div>
            {readiness.note && (
              <div className="mt-2 text-[11px] text-muted-foreground">{readiness.note}</div>
            )}
          </div>
        )}

        {/* RC1.3.2A · Composition rationale (small, subtle). */}
        {composition && (
          <div className="mt-4 flex items-start gap-2 text-[11px] text-muted-foreground">
            <Route className="h-3 w-3 mt-0.5 text-primary/80 shrink-0" />
            <div>
              <span className="text-foreground/80 font-medium">Today's shape:</span>{' '}
              {composition.rationale || `${composition.primary_kind}, ${composition.practice_count} practice`}
              {continuity && continuity.level && continuity.level !== 'unknown' && (
                <span className="ml-2">
                  · continuity: <span className="text-foreground/80">{String(continuity.level).replace('_', ' ')}</span>
                </span>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
