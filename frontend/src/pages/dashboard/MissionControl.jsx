import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import {
  Target, Flame, ShieldCheck, RefreshCcw, GraduationCap,
  Activity, Bell, Sparkles, Check, SkipForward, Loader2,
  CheckCircle2, Circle, Clock, Zap, TrendingUp, ChevronDown, Building2,
} from 'lucide-react';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import { DASHBOARD } from '@/constants/testIds';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardService, missionService, knowledgeService } from '@/services/mission.service';
import { TARGET_COMPANIES } from '@/config/companies';
import { formatApiError } from '@/utils/formatApiError';
import { cn } from '@/lib/utils';

const ACTIVITY_META = {
  mission_completed:  { dot: 'bg-emerald-400',  label: 'Mission completed' },
  mission_skipped:    { dot: 'bg-amber-400',    label: 'Mission skipped' },
  task_completed:     { dot: 'bg-primary',      label: 'Task completed' },
  task_uncompleted:   { dot: 'bg-white/40',     label: 'Task uncompleted' },
  problem_feedback:   { dot: 'bg-secondary',    label: 'Problem feedback' },
  practice_more:      { dot: 'bg-secondary',    label: 'Practice more' },
  profile_updated:    { dot: 'bg-secondary',    label: 'Profile updated' },
  settings_changed:   { dot: 'bg-secondary',    label: 'Settings changed' },
  daily_login:        { dot: 'bg-white/40',     label: 'Signed in' },
  mission_generated:  { dot: 'bg-primary',      label: 'Mission generated' },
};

function WidgetHeader({ icon: Icon, title, action }) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div className="flex items-center gap-2.5">
        <span className="h-8 w-8 rounded-lg border border-white/10 bg-white/[0.03] flex items-center justify-center">
          <Icon className="h-4 w-4 text-primary" />
        </span>
        <h3 className="font-display text-base font-medium">{title}</h3>
      </div>
      {action}
    </div>
  );
}

function difficultyChipClass(d) {
  if (d === 'easy')   return 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300';
  if (d === 'hard')   return 'border-rose-400/30 bg-rose-400/10 text-rose-300';
  return 'border-amber-400/30 bg-amber-400/10 text-amber-300';
}

function taskKindIcon(kind) {
  if (kind === 'practice') return <Zap className="h-3.5 w-3.5" />;
  if (kind === 'revise')   return <RefreshCcw className="h-3.5 w-3.5" />;
  return <GraduationCap className="h-3.5 w-3.5" />;
}

export default function MissionControl() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busyTask, setBusyTask] = useState(null);
  const [busyAction, setBusyAction] = useState(null);
  const [tree, setTree] = useState(null);
  const [expandedDomain, setExpandedDomain] = useState(null);

  const load = useCallback(async () => {
    try {
      const d = await dashboardService.get();
      setData(d);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const ensureTree = async () => {
    if (tree) return;
    try {
      const t = await knowledgeService.tree();
      setTree(t);
    } catch (e) { toast.error(formatApiError(e)); }
  };

  const onToggleTask = async (taskId) => {
    if (!data) return;
    setBusyTask(taskId);
    try {
      await missionService.toggleTask(data.mission.id, taskId);
      await load();
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setBusyTask(null);
    }
  };

  const onCompleteMission = async () => {
    if (!data) return;
    setBusyAction('complete');
    try {
      await missionService.completeMission(data.mission.id);
      toast.success('Mission completed. Streak updated.');
      await load();
    } catch (err) {
      toast.error(formatApiError(err));
    } finally { setBusyAction(null); }
  };

  const onSkipMission = async () => {
    if (!data) return;
    setBusyAction('skip');
    try {
      await missionService.skipMission(data.mission.id);
      toast('Mission skipped.', { icon: <SkipForward className="h-4 w-4" /> });
      await load();
    } catch (err) {
      toast.error(formatApiError(err));
    } finally { setBusyAction(null); }
  };

  if (loading || !data) {
    return (
      <div className="py-24 flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="overline">Loading workspace</span>
      </div>
    );
  }

  const { mission, streak, readiness, knowledge, revisions, activity, onboarding, adjustment, company_readiness } = data;
  const tasks = mission.tasks || [];
  const doneCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length || 1;
  const progressPct = Math.round((doneCount / totalCount) * 100);
  const missionCompleted = mission.status === 'completed';
  const missionSkipped = mission.status === 'skipped';

  const targetCompanies = (onboarding.target_companies || [])
    .map((id) => TARGET_COMPANIES.find((c) => c.id === id))
    .filter(Boolean);

  return (
    <div className="space-y-6" data-testid={DASHBOARD.root}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4"
      >
        <div>
          <div className="overline mb-2">Mission Control</div>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">
            Welcome back, {user?.name?.split(' ')[0]}.
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Calibrated for {targetCompanies.length || '—'} target {targetCompanies.length === 1 ? 'company' : 'companies'}
            {onboarding.days_to_target != null && <> · {onboarding.days_to_target} days to target</>}.
          </p>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-muted-foreground">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          Adaptive Engine · v2
        </div>
      </motion.div>

      {/* Adaptive banner */}
      {adjustment && adjustment.reason && (
        <motion.div
          initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }}
          data-testid="dashboard-adaptive-banner"
          className={cn(
            'rounded-xl border px-4 py-3 flex items-start gap-3',
            adjustment.mode === 'revise'  && 'border-amber-400/30 bg-amber-400/[0.06]',
            adjustment.mode === 'advance' && 'border-emerald-400/30 bg-emerald-400/[0.06]',
            (!adjustment.mode || adjustment.mode === 'continue') && 'border-primary/25 bg-primary/[0.06]',
          )}
        >
          <TrendingUp className="h-4 w-4 mt-0.5 shrink-0 text-primary" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="overline text-primary">Adaptive plan</span>
              {adjustment.mode && (
                <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground border border-white/10 rounded-full px-2 py-0.5">
                  {adjustment.mode}
                </span>
              )}
            </div>
            <p className="text-sm">{adjustment.reason}</p>
            {adjustment.inserted_prerequisites?.length > 0 && (
              <p className="text-xs text-muted-foreground mt-1">
                Prerequisite revisions inserted: {adjustment.inserted_prerequisites.join(', ')}.
              </p>
            )}
          </div>
        </motion.div>
      )}

      {/* Bento grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {/* Today's Mission — hero */}
        <GlassCard
          data-testid={DASHBOARD.widgetTodayMission}
          className="p-6 md:col-span-2 lg:col-span-2 lg:row-span-2 relative overflow-hidden"
        >
          <div className="absolute -top-24 -right-24 h-56 w-56 rounded-full bg-primary/10 blur-3xl" />
          <WidgetHeader
            icon={Target}
            title="Today's Mission"
            action={
              <span className={cn('px-2 py-0.5 rounded-full text-[11px] font-mono uppercase tracking-wider border',
                missionCompleted ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300'
                : missionSkipped ? 'border-amber-400/30 bg-amber-400/10 text-amber-300'
                : 'border-primary/30 bg-primary/10 text-primary')}
              >
                {missionCompleted ? 'Completed' : missionSkipped ? 'Skipped' : 'In progress'}
              </span>
            }
          />
          <div className="mt-1">
            <h2 className="font-display text-2xl font-semibold tracking-tight leading-snug max-w-lg">
              {mission.title}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-md">
              {mission.learning_objective}
            </p>
            <div className="mt-6 grid grid-cols-3 gap-6">
              <div>
                <div className="overline mb-1">Focus</div>
                <div className="text-sm font-medium">{mission.focus_area}</div>
              </div>
              <div>
                <div className="overline mb-1">Est. time</div>
                <div className="text-sm font-medium flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                  {Math.round(mission.estimated_duration_minutes / 60 * 10) / 10} h
                </div>
              </div>
              <div>
                <div className="overline mb-1">Difficulty</div>
                <span className={cn('inline-block px-2 py-0.5 rounded-md text-xs border capitalize', difficultyChipClass(mission.difficulty))}>
                  {mission.difficulty}
                </span>
              </div>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="overline">Progress</span>
                <span className="font-mono text-xs text-muted-foreground">{doneCount} / {tasks.length}</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-primary to-secondary"
                  animate={{ width: `${progressPct}%` }}
                  transition={{ type: 'spring', stiffness: 200, damping: 30 }}
                />
              </div>
            </div>

            {/* Tasks */}
            <div className="mt-5 space-y-2">
              {tasks.map((t) => {
                const isBusy = busyTask === t.id;
                const isPractice = t.kind === 'practice' && t.pattern;
                return (
                  <div key={t.id} className="flex items-stretch gap-2">
                    <button
                      onClick={() => !missionSkipped && onToggleTask(t.id)}
                      disabled={missionSkipped || isBusy}
                      data-testid={`mission-task-${t.id}`}
                      className={cn(
                        'group flex-1 text-left flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors',
                        t.completed
                          ? 'border-emerald-400/40 bg-emerald-400/[0.12] hover:bg-emerald-400/[0.16]'
                          : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/[0.12]',
                      )}
                    >
                      <span className={cn('h-5 w-5 rounded-full border flex items-center justify-center shrink-0 transition-colors',
                        t.completed ? 'border-emerald-400 bg-emerald-400 text-emerald-950' : 'border-white/15')}>
                        {isBusy ? <Loader2 className="h-3 w-3 animate-spin" />
                          : t.completed ? <Check className="h-3 w-3" strokeWidth={3} />
                          : <Circle className="h-2 w-2" />}
                      </span>
                      <span className="flex-1 text-sm text-foreground">
                        {t.title}
                      </span>
                      <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-mono text-muted-foreground uppercase tracking-wider">
                        {taskKindIcon(t.kind)}
                        {t.kind}
                      </span>
                    </button>
                    {isPractice && (
                      <a
                        href="/app/coding-arena"
                        data-testid={`mission-task-arena-${t.id}`}
                        className="inline-flex items-center gap-1.5 px-3 rounded-lg border border-primary/30 bg-primary/10 hover:bg-primary/15 text-xs font-medium text-primary transition-colors"
                      >
                        Open Arena
                      </a>
                    )}
                  </div>
                );
              })}
            </div>

            {!missionCompleted && !missionSkipped && (
              <div className="mt-6 flex flex-wrap gap-2.5">
                <button
                  onClick={onCompleteMission} disabled={busyAction === 'complete'}
                  data-testid="mission-complete-button"
                  className="h-10 px-4 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium btn-primary-glow disabled:opacity-60 transition-colors inline-flex items-center gap-2"
                >
                  {busyAction === 'complete'
                    ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Completing…</>
                    : <><CheckCircle2 className="h-3.5 w-3.5" />Mark mission complete</>}
                </button>
                <button
                  onClick={onSkipMission} disabled={busyAction === 'skip'}
                  data-testid="mission-skip-button"
                  className="h-10 px-4 rounded-lg border border-white/[0.1] hover:bg-white/[0.04] text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-2"
                >
                  {busyAction === 'skip'
                    ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Skipping…</>
                    : <><SkipForward className="h-3.5 w-3.5" />Skip today</>}
                </button>
              </div>
            )}
            {missionCompleted && (
              <div className="mt-6 flex items-center gap-2 text-sm text-emerald-300">
                <CheckCircle2 className="h-4 w-4" />
                Nice work — mission logged. Tomorrow's plan adapts to today's confidence.
              </div>
            )}
            {missionSkipped && (
              <div className="mt-6 flex items-center gap-2 text-sm text-amber-300">
                <SkipForward className="h-4 w-4" />
                Skipped for today. Streak will reset unless you complete tomorrow's mission.
              </div>
            )}
          </div>
        </GlassCard>

        {/* Interview Readiness */}
        <GlassCard data-testid={DASHBOARD.widgetReadiness} className="p-6">
          <WidgetHeader icon={ShieldCheck} title="Interview Readiness" />
          <div className="flex items-end gap-3">
            <span className="font-display text-4xl font-semibold tracking-tight">
              {Math.round(readiness)}<span className="text-lg text-muted-foreground">%</span>
            </span>
            <span className={cn('text-xs mb-1', readiness >= 70 ? 'text-emerald-400' : readiness >= 40 ? 'text-amber-400' : 'text-muted-foreground')}>
              {readiness >= 70 ? 'On track' : readiness >= 40 ? 'Building' : 'Baseline'}
            </span>
          </div>
          <div className="mt-4 h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
            <motion.div className="h-full bg-gradient-to-r from-primary to-secondary"
              animate={{ width: `${readiness}%` }} transition={{ type: 'spring', stiffness: 200, damping: 30 }} />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">Weighted across DSA · Java · LLD · HLD · Core CS.</p>
        </GlassCard>

        {/* Study Streak */}
        <GlassCard data-testid={DASHBOARD.widgetStreak} className="p-6">
          <WidgetHeader icon={Flame} title="Study Streak" />
          <div className="flex items-baseline gap-2">
            <span className="font-display text-4xl font-semibold tracking-tight">{streak.current}</span>
            <span className="text-sm text-muted-foreground">days</span>
          </div>
          <div className="mt-4 flex gap-1.5">
            {streak.week_grid.map((active, i) => (
              <span key={i}
                className={cn('flex-1 h-5 rounded-md border',
                  active ? 'bg-primary/40 border-primary/50' : 'bg-white/[0.04] border-white/[0.06]')}
              />
            ))}
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            {streak.current > 0 ? `Longest streak · ${streak.longest} days` : 'Complete today\'s mission to start.'}
          </p>
        </GlassCard>

        {/* Company Readiness */}
        <GlassCard data-testid="dashboard-widget-company-readiness" className="p-6 md:col-span-1 lg:col-span-2">
          <WidgetHeader icon={Building2} title="Company Readiness" />
          {company_readiness?.length ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-2.5">
              {company_readiness.map((c) => {
                const meta = TARGET_COMPANIES.find((x) => x.id === c.company_id);
                if (!meta) return null;
                return (
                  <div key={c.company_id} className="flex items-center gap-3">
                    <span
                      className="h-7 w-7 rounded-md border border-white/10 flex items-center justify-center font-mono text-xs shrink-0"
                      style={{ background: `${meta.accent}20`, color: meta.accent === '#000000' ? '#fff' : meta.accent }}
                    >
                      {meta.name[0]}
                    </span>
                    <span className="text-sm flex-1 flex items-center gap-1.5">
                      {meta.name}
                      {c.is_target && (
                        <span className="text-[9px] font-mono text-primary uppercase tracking-widest">Target</span>
                      )}
                    </span>
                    <div className="w-24 h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                      <div className="h-full bg-primary/80" style={{ width: `${c.score}%` }} />
                    </div>
                    <span className="font-mono text-xs text-muted-foreground w-10 text-right">
                      {Math.round(c.score)}%
                    </span>
                  </div>
                );
              })}
            </div>
          ) : <p className="text-sm text-muted-foreground">Set target companies to see readiness.</p>}
        </GlassCard>

        {/* Upcoming Revision */}
        <GlassCard data-testid={DASHBOARD.widgetRevision} className="p-6 md:col-span-1 lg:col-span-2">
          <WidgetHeader icon={RefreshCcw} title="Upcoming Revision" />
          {revisions.length === 0 ? (
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4 text-sm text-muted-foreground">
              No revisions queued yet. They'll appear once you complete tasks.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {revisions.slice(0, 3).map((r) => (
                <div key={r.id} className={cn(
                  'rounded-lg border p-3',
                  r.is_due ? 'border-primary/30 bg-primary/[0.06]' : 'border-white/[0.06] bg-white/[0.02]',
                )}>
                  <div className="overline mb-1">
                    {r.is_due ? 'Due now' : `In ${Math.max(1, Math.ceil((new Date(r.next_review_date) - new Date()) / 86400000))}d`}
                  </div>
                  <p className="text-sm line-clamp-2">{r.task_title}</p>
                </div>
              ))}
            </div>
          )}
          <p className="mt-4 text-xs text-muted-foreground">Spaced repetition · 1d → 3d → 7d → 14d → 30d → 60d (confidence-adjusted).</p>
        </GlassCard>

        {/* Knowledge Progress — drill-down */}
        <GlassCard data-testid={DASHBOARD.widgetKnowledge} className="p-6 md:col-span-2 lg:col-span-2">
          <WidgetHeader
            icon={GraduationCap}
            title="Knowledge Progress"
            action={
              <span className="text-[11px] font-mono text-muted-foreground uppercase tracking-wider">
                Click to drill down
              </span>
            }
          />
          <div className="space-y-2.5">
            {knowledge.map((k) => {
              const expanded = expandedDomain === k.topic;
              const subs = tree?.find((d) => d.domain === k.topic)?.subtopics || [];
              return (
                <div key={k.topic}>
                  <button
                    onClick={async () => {
                      await ensureTree();
                      setExpandedDomain(expanded ? null : k.topic);
                    }}
                    data-testid={`knowledge-domain-${k.topic}`}
                    className="w-full text-left rounded-lg border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] px-3 py-2 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm flex items-center gap-2">
                        <ChevronDown className={cn('h-3.5 w-3.5 transition-transform', expanded && 'rotate-180')} />
                        {k.label}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        {Math.round(k.score)}%{k.completions > 0 && <span className="ml-1 text-primary">· {k.completions}✓</span>}
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                      <div className="h-full bg-primary/80" style={{ width: `${k.score}%` }} />
                    </div>
                  </button>
                  <AnimatePresence>
                    {expanded && subs.length > 0 && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }} className="overflow-hidden"
                      >
                        <div className="pl-6 pr-2 py-2 space-y-2">
                          {subs.map((s, i) => (
                            <div key={`${k.topic}-${s.pattern || s.label}-${i}`}
                              className="rounded-md border border-white/[0.04] bg-white/[0.015] px-3 py-2">
                              <div className="flex items-center justify-between text-xs mb-1">
                                <span>{s.label}</span>
                                <span className="font-mono text-muted-foreground">
                                  {Math.round(s.progress)}%
                                  {s.problems_solved > 0 && <span className="ml-1.5">· {s.problems_solved}✓</span>}
                                  {s.avg_confidence != null && <span className="ml-1.5">· conf {s.avg_confidence}</span>}
                                </span>
                              </div>
                              <div className="h-1 rounded-full bg-white/[0.04] overflow-hidden">
                                <div className={cn('h-full',
                                  s.revision_status === 'due' ? 'bg-amber-400/80' :
                                  s.revision_status === 'mastered' ? 'bg-emerald-400/80' : 'bg-primary/70')}
                                  style={{ width: `${s.progress}%` }} />
                              </div>
                              <div className="mt-1 flex items-center gap-2">
                                <span className={cn('text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded-sm',
                                  s.revision_status === 'due' ? 'text-amber-300 bg-amber-400/10' :
                                  s.revision_status === 'mastered' ? 'text-emerald-300 bg-emerald-400/10' :
                                  'text-muted-foreground bg-white/[0.03]')}>
                                  {s.revision_status}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Recent Activity — latest 5 */}
        <GlassCard data-testid={DASHBOARD.widgetActivity} className="p-6 md:col-span-2 lg:col-span-2">
          <WidgetHeader icon={Activity} title="Recent Activity" />
          {activity.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nothing yet — start today's mission.</p>
          ) : (
            <div className="space-y-3">
              {activity.slice(0, 5).map((e) => {
                const meta = ACTIVITY_META[e.kind] || { dot: 'bg-white/30' };
                return (
                  <div key={e.id} className="flex items-center gap-3 text-sm">
                    <span className={cn('h-2 w-2 rounded-full shrink-0', meta.dot)} />
                    <span className="flex-1 truncate">{e.title}</span>
                    <span className="text-xs text-muted-foreground font-mono whitespace-nowrap">
                      {formatDistanceToNow(parseISO(e.ts), { addSuffix: true })}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </GlassCard>

        {/* Notifications preview */}
        <GlassCard data-testid={DASHBOARD.widgetNotifications} className="p-6 md:col-span-2 lg:col-span-2">
          <WidgetHeader
            icon={Bell} title="Notifications"
            action={
              <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-[11px] font-mono text-primary">
                {revisions.filter((r) => r.is_due).length} due
              </span>
            }
          />
          <div className="space-y-2.5">
            <div className="rounded-lg border border-primary/30 bg-primary/[0.06] p-3">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                <span className="text-sm font-medium">Today's mission generated</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Focus · {mission.focus_area}. Estimated {Math.round(mission.estimated_duration_minutes / 60 * 10) / 10} hours.
              </p>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-sm font-medium mb-0.5">Target date locked</div>
              <p className="text-xs text-muted-foreground">
                {onboarding.interview_target_date
                  ? `Aiming for ${format(parseISO(onboarding.interview_target_date), 'PPP')}.`
                  : 'No target date set yet.'}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
