import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar as CalendarIcon, Loader2, Zap, CheckCircle2, Code2, BookOpen, RefreshCw, Sparkles, Target, TrendingUp } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { dashboardService } from '@/services/mission.service';
import { cn } from '@/lib/utils';
import { DASHBOARD } from '@/constants/testIds';

const CATEGORY_META = {
  missions:    { label: 'Missions',    icon: Target,       color: 'from-primary/70 to-primary/40' },
  tasks:       { label: 'Tasks',       icon: CheckCircle2, color: 'from-emerald-400/70 to-emerald-500/40' },
  coding:      { label: 'Coding',      icon: Code2,        color: 'from-sky-400/70 to-sky-500/40' },
  topics:      { label: 'Topics',      icon: BookOpen,     color: 'from-violet-400/70 to-violet-500/40' },
  revisions:   { label: 'Revisions',   icon: RefreshCw,    color: 'from-amber-400/70 to-amber-500/40' },
  knowledge:   { label: 'Knowledge',   icon: Zap,          color: 'from-fuchsia-400/70 to-fuchsia-500/40' },
  mentor:      { label: 'Mentor',      icon: Sparkles,     color: 'from-indigo-400/70 to-indigo-500/40' },
  confidence:  { label: 'Confidence',  icon: TrendingUp,   color: 'from-cyan-400/70 to-cyan-500/40' },
};

export function WeeklyActivityWidget() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    dashboardService.weeklyActivity()
      .then((d) => { if (mounted) setData(d); })
      .catch(() => { if (mounted) setData({ days: [], totals: {}, grand_total: 0, max_day_total: 0, categories: [] }); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <GlassCard className="p-6" data-testid={DASHBOARD.widgetWeeklyActivity}>
        <div className="flex items-center gap-2.5 mb-4">
          <span className="h-8 w-8 rounded-lg border hairline bg-foreground/[0.03] flex items-center justify-center">
            <CalendarIcon className="h-4 w-4 text-primary" />
          </span>
          <h3 className="font-display text-base font-medium">This Week's Activity</h3>
        </div>
        <div className="h-32 flex items-center justify-center text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
        </div>
      </GlassCard>
    );
  }

  const days = data?.days || [];
  const totals = data?.totals || {};
  const maxDayTotal = Math.max(1, data?.max_day_total || 0);
  const grandTotal = data?.grand_total || 0;
  const activeCategories = (data?.categories || []).filter((c) => totals[c] > 0);

  const empty = grandTotal === 0;

  return (
    <GlassCard className="p-6" data-testid={DASHBOARD.widgetWeeklyActivity}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <span className="h-8 w-8 rounded-lg border hairline bg-foreground/[0.03] flex items-center justify-center">
            <CalendarIcon className="h-4 w-4 text-primary" />
          </span>
          <div>
            <h3 className="font-display text-base font-medium">This Week's Activity</h3>
            <p className="text-[11px] text-muted-foreground">Last 7 days across all learning surfaces</p>
          </div>
        </div>
        <div className="text-right">
          <div className="font-display text-xl font-semibold tracking-tight">{grandTotal}</div>
          <div className="overline mt-0.5">Events</div>
        </div>
      </div>

      {empty ? (
        <div className="rounded-lg border hairline bg-foreground/[0.02] p-6 text-center text-sm text-muted-foreground">
          No activity yet this week — complete a task, solve a problem, or ask the Mentor to see your week come alive.
        </div>
      ) : (
        <>
          {/* Stacked bar chart */}
          <div className="grid grid-cols-7 gap-1.5 sm:gap-2 items-end h-32">
            {days.map((d, idx) => {
              const totalHeight = Math.max(4, (d.total / maxDayTotal) * 100);
              return (
                <div key={d.date} className="flex flex-col items-center gap-1.5 h-full justify-end">
                  <div className="w-full h-full flex flex-col justify-end rounded-md overflow-hidden bg-foreground/[0.03]" title={`${d.label} · ${d.total} events`}>
                    {d.total > 0 ? (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${totalHeight}%` }}
                        transition={{ delay: idx * 0.04, duration: 0.4, ease: 'easeOut' }}
                        className="w-full flex flex-col overflow-hidden"
                      >
                        {(data.categories || []).map((cat) => {
                          const count = d.counts?.[cat] || 0;
                          if (!count) return null;
                          const meta = CATEGORY_META[cat] || { color: 'from-primary/70 to-primary/40' };
                          const share = (count / d.total) * 100;
                          return (
                            <div
                              key={cat}
                              className={cn('bg-gradient-to-b w-full', meta.color)}
                              style={{ height: `${share}%` }}
                              title={`${meta.label || cat}: ${count}`}
                            />
                          );
                        })}
                      </motion.div>
                    ) : (
                      <div className="h-1 w-full bg-foreground/[0.06] rounded" />
                    )}
                  </div>
                  <div className="text-[10px] font-mono text-muted-foreground">{d.label[0]}</div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-x-3 gap-y-1.5">
            {activeCategories.map((cat) => {
              const meta = CATEGORY_META[cat] || { label: cat, icon: Sparkles, color: 'from-primary/70 to-primary/40' };
              const Icon = meta.icon;
              return (
                <div key={cat} className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                  <span className={cn('h-2.5 w-2.5 rounded bg-gradient-to-b', meta.color)} />
                  <Icon className="h-3 w-3" />
                  <span>{meta.label}</span>
                  <span className="font-mono text-foreground/80">{totals[cat] || 0}</span>
                </div>
              );
            })}
          </div>
        </>
      )}
    </GlassCard>
  );
}
