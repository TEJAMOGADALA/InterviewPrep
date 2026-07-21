import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import {
  Target, Flame, ShieldCheck, RefreshCcw, GraduationCap,
  Activity, Bell, ArrowRight, Sparkles, Check, SkipForward, Loader2,
  CheckCircle2, Circle, Clock, Zap,
} from 'lucide-react';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import { DASHBOARD } from '@/constants/testIds';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardService, missionService } from '@/services/mission.service';
import { TARGET_COMPANIES } from '@/config/companies';
import { formatApiError } from '@/utils/formatApiError';
import { cn } from '@/lib/utils';

const ACTIVITY_META = {
  mission_completed:  { dot: 'bg-emerald-400',  label: 'Mission completed' },
  mission_skipped:    { dot: 'bg-amber-400',    label: 'Mission skipped' },
  task_completed:     { dot: 'bg-primary',      label: 'Task completed' },
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

  const onCompleteTask = async (taskId) => {
    if (!data) return;
    setBusyTask(taskId);
    try {
      await missionService.completeTask(data.mission.id, taskId);
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
    } finally {
      setBusyAction(null);
    }
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
    } finally {
      setBusyAction(null);
    }
  };

  if (loading || !data) {
    return (
      <div className="py-24 flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="overline">Loading workspace</span>
      </div>
    );
  }

  const { mission, streak, readiness, knowledge, revisions, activity, onboarding } = data;
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
          System online · Mission Engine v1
        </div>
      </motion.div>

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

            {/* Progress */}
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
                return (
                  <button
                    key={t.id}
                    onClick={() => !t.completed && !missionCompleted && !missionSkipped && onCompleteTask(t.id)}
                    disabled={t.completed || missionCompleted || missionSkipped || isBusy}
                    data-testid={`mission-task-${t.id}`}
                    className={cn(
                      'group w-full text-left flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors',
                      t.completed
                        ? 'border-emerald-400/20 bg-emerald-400/[0.06]'
                        : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/[0.12]',
                    )}
                  >
                    <span className={cn('h-5 w-5 rounded-full border flex items-center justify-center shrink-0',
                      t.completed ? 'border-emerald-400 bg-emerald-400/20 text-emerald-300' : 'border-white/15')}>
                      {isBusy ? <Loader2 className="h-3 w-3 animate-spin" />
                        : t.completed ? <Check className="h-3 w-3" />
                        : <Circle className="h-2 w-2" />}
                    </span>
                    <span className={cn('flex-1 text-sm', t.completed && 'line-through text-muted-foreground')}>
                      {t.title}
                    </span>
                    <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-mono text-muted-foreground uppercase tracking-wider">
                      {taskKindIcon(t.kind)}
                      {t.kind}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Actions */}
            {!missionCompleted && !missionSkipped && (
              <div className="mt-6 flex flex-wrap gap-2.5">
                <button
                  onClick={onCompleteMission}
                  disabled={busyAction === 'complete'}
                  data-testid="mission-complete-button"
                  className="h-10 px-4 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium btn-primary-glow disabled:opacity-60 transition-colors inline-flex items-center gap-2"
                >
                  {busyAction === 'complete'
                    ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Completing…</>
                    : <><CheckCircle2 className="h-3.5 w-3.5" />Mark mission complete</>}
                </button>
                <button
                  onClick={onSkipMission}
                  disabled={busyAction === 'skip'}
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
                Nice work — mission logged. New mission arrives at 00:00 UTC.
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
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-secondary"
              animate={{ width: `${readiness}%` }}
              transition={{ type: 'spring', stiffness: 200, damping: 30 }}
            />
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
              <span
                key={i}
                className={cn(
                  'flex-1 h-5 rounded-md border',
                  active ? 'bg-primary/40 border-primary/50' : 'bg-white/[0.04] border-white/[0.06]',
                )}
                title={active ? 'Active' : ''}
              />
            ))}
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            {streak.current > 0 ? `Longest streak · ${streak.longest} days` : 'Complete today\'s mission to start.'}
          </p>
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
                    {r.is_due ? 'Due now' : `In ${Math.max(1, Math.ceil((new Date(r.next_review_date) - new Date()) / (86400000)))}d`}
                  </div>
                  <p className="text-sm line-clamp-2">{r.task_title}</p>
                </div>
              ))}
            </div>
          )}
          <p className="mt-4 text-xs text-muted-foreground">Spaced repetition · 1d → 3d → 7d → 14d → 30d.</p>
        </GlassCard>

        {/* Knowledge Progress */}
        <GlassCard data-testid={DASHBOARD.widgetKnowledge} className="p-6 md:col-span-2">
          <WidgetHeader icon={GraduationCap} title="Knowledge Progress" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-3">
            {knowledge.map((k) => (
              <div key={k.topic}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-sm">{k.label}</span>
                  <span className="font-mono text-xs text-muted-foreground">
                    {Math.round(k.score)}%{k.completions > 0 && <span className="ml-1 text-primary">· {k.completions}✓</span>}
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                  <div className="h-full bg-primary/80" style={{ width: `${k.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Recent Activity */}
        <GlassCard data-testid={DASHBOARD.widgetActivity} className="p-6 md:col-span-2">
          <WidgetHeader icon={Activity} title="Recent Activity" />
          {activity.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nothing yet — start today's mission.</p>
          ) : (
            <div className="space-y-3">
              {activity.slice(0, 6).map((e) => {
                const meta = ACTIVITY_META[e.kind] || { dot: 'bg-white/30', label: e.kind };
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
        <GlassCard data-testid={DASHBOARD.widgetNotifications} className="p-6 md:col-span-1 lg:col-span-2">
          <WidgetHeader
            icon={Bell}
            title="Notifications"
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
