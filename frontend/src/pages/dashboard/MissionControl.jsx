import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Target, Flame, ShieldCheck, RefreshCcw, GraduationCap,
  Activity, Bell, ArrowRight, Sparkles,
} from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { DASHBOARD } from '@/constants/testIds';
import { useAuth } from '@/contexts/AuthContext';
import { userService } from '@/services/auth.service';
import { TARGET_COMPANIES } from '@/config/companies';
import { format, formatDistanceToNow } from 'date-fns';

function StatChip({ label, value, tone = 'default' }) {
  const tones = {
    default: 'text-foreground',
    up: 'text-emerald-400',
    warn: 'text-amber-400',
  };
  return (
    <div className="flex flex-col">
      <span className="overline">{label}</span>
      <span className={`font-display text-2xl font-semibold tracking-tight ${tones[tone]}`}>{value}</span>
    </div>
  );
}

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

export default function MissionControl() {
  const { user } = useAuth();
  const [onboarding, setOnboarding] = useState(null);

  useEffect(() => {
    userService.getOnboarding().then(setOnboarding).catch(() => setOnboarding(null));
  }, []);

  const targetCompanies = (onboarding?.target_companies || [])
    .map((id) => TARGET_COMPANIES.find((c) => c.id === id))
    .filter(Boolean);

  const daysToTarget = onboarding?.interview_target_date
    ? Math.max(0, Math.ceil((new Date(onboarding.interview_target_date) - new Date()) / (1000 * 60 * 60 * 24)))
    : null;

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
            Your workspace is calibrated for {targetCompanies.length || '—'} target {targetCompanies.length === 1 ? 'company' : 'companies'}
            {daysToTarget !== null && <> · {daysToTarget} days to target</>}.
          </p>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-muted-foreground">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          System online · Phase 1
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
              <button className="text-xs font-mono uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors">
                View brief
              </button>
            }
          />
          <div className="mt-2">
            <h2 className="font-display text-2xl font-semibold tracking-tight leading-snug max-w-md">
              Your first mission unlocks with the Mission Engine.
            </h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-md">
              The engine will schedule targeted DSA, LLD, HLD and system fundamentals based on your baseline. Ships in the next drop.
            </p>
            <div className="mt-6 grid grid-cols-3 gap-6">
              <StatChip label="Focus block" value="—" />
              <StatChip label="Est. time" value="—" />
              <StatChip label="Difficulty" value="—" />
            </div>
            <button className="mt-8 inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors">
              Preview mission types <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </GlassCard>

        {/* Interview Readiness */}
        <GlassCard data-testid={DASHBOARD.widgetReadiness} className="p-6">
          <WidgetHeader icon={ShieldCheck} title="Interview Readiness" />
          <div className="flex items-end gap-3">
            <span className="font-display text-4xl font-semibold tracking-tight">42<span className="text-lg text-muted-foreground">%</span></span>
            <span className="text-xs text-amber-400 mb-1">Baseline</span>
          </div>
          <div className="mt-4 h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
            <div className="h-full w-[42%] bg-gradient-to-r from-primary to-secondary" />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">Recalculates after each mission completes.</p>
        </GlassCard>

        {/* Study Streak */}
        <GlassCard data-testid={DASHBOARD.widgetStreak} className="p-6">
          <WidgetHeader icon={Flame} title="Study Streak" />
          <div className="flex items-baseline gap-2">
            <span className="font-display text-4xl font-semibold tracking-tight">0</span>
            <span className="text-sm text-muted-foreground">days</span>
          </div>
          <div className="mt-4 flex gap-1.5">
            {Array.from({ length: 7 }).map((_, i) => (
              <span key={i} className="flex-1 h-5 rounded-md bg-white/[0.04] border border-white/[0.06]" />
            ))}
          </div>
          <p className="mt-3 text-xs text-muted-foreground">Complete today's mission to start.</p>
        </GlassCard>

        {/* Upcoming Revision */}
        <GlassCard data-testid={DASHBOARD.widgetRevision} className="p-6 md:col-span-1 lg:col-span-2">
          <WidgetHeader icon={RefreshCcw} title="Upcoming Revision" />
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {['Trees & Recursion', 'Design a URL Shortener', 'OS · Deadlocks'].map((t) => (
              <div key={t} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                <div className="overline mb-1">Queued</div>
                <p className="text-sm">{t}</p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs text-muted-foreground">Spaced-repetition engine populates this daily.</p>
        </GlassCard>

        {/* Knowledge Progress */}
        <GlassCard data-testid={DASHBOARD.widgetKnowledge} className="p-6 md:col-span-2">
          <WidgetHeader icon={GraduationCap} title="Knowledge Progress" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {['DSA', 'LLD', 'HLD', 'Fundamentals'].map((k, i) => {
              const pct = onboarding
                ? [
                    onboarding.self_assessment.dsa,
                    onboarding.self_assessment.lld,
                    onboarding.self_assessment.hld,
                    Math.round(
                      (onboarding.self_assessment.operating_systems +
                        onboarding.self_assessment.dbms +
                        onboarding.self_assessment.computer_networks) / 3,
                    ),
                  ][i] * 10
                : 0;
              return (
                <div key={k}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm">{k}</span>
                    <span className="font-mono text-xs text-muted-foreground">{pct}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                    <div className="h-full bg-primary/80" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Recent Activity */}
        <GlassCard data-testid={DASHBOARD.widgetActivity} className="p-6 md:col-span-2">
          <WidgetHeader icon={Activity} title="Recent Activity" />
          <div className="space-y-3">
            {[
              { t: 'Workspace initialized', ts: onboarding?.created_at, kind: 'system' },
              { t: 'Profile created', ts: user?.created_at, kind: 'account' },
              { t: 'Mission Engine · pending activation', ts: null, kind: 'pending' },
            ].map((e, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <span
                  className={
                    'h-2 w-2 rounded-full ' +
                    (e.kind === 'pending' ? 'bg-amber-400' : 'bg-primary')
                  }
                />
                <span className="flex-1">{e.t}</span>
                <span className="text-xs text-muted-foreground font-mono">
                  {e.ts ? formatDistanceToNow(new Date(e.ts), { addSuffix: true }) : '—'}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Notifications preview */}
        <GlassCard data-testid={DASHBOARD.widgetNotifications} className="p-6 md:col-span-1 lg:col-span-2">
          <WidgetHeader
            icon={Bell}
            title="Notifications"
            action={
              <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-[11px] font-mono text-primary">
                1 new
              </span>
            }
          />
          <div className="space-y-2.5">
            <div className="rounded-lg border border-primary/30 bg-primary/[0.06] p-3">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                <span className="text-sm font-medium">Foundation build ready</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Your workspace is initialized. The Mission Engine ships in Phase 2.
              </p>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="text-sm font-medium mb-0.5">Target date locked</div>
              <p className="text-xs text-muted-foreground">
                {onboarding?.interview_target_date
                  ? `Aiming for ${format(new Date(onboarding.interview_target_date), 'PPP')}.`
                  : 'No target date set yet.'}
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
