import { useEffect, useState } from 'react';
import { formatDistanceToNow, parseISO } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import {
  Bell, Sparkles, CheckCircle2, SkipForward, Zap, User as UserIcon,
  Settings as SettingsIcon, LogIn, Target, Loader2,
} from 'lucide-react';
import { activityService } from '@/services/mission.service';
import { formatApiError } from '@/utils/formatApiError';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const KIND_META = {
  mission_completed:  { icon: CheckCircle2,  tone: 'emerald' },
  mission_skipped:    { icon: SkipForward,   tone: 'amber' },
  task_completed:     { icon: Zap,           tone: 'primary' },
  profile_updated:    { icon: UserIcon,      tone: 'secondary' },
  settings_changed:   { icon: SettingsIcon,  tone: 'secondary' },
  daily_login:        { icon: LogIn,         tone: 'muted' },
  mission_generated:  { icon: Target,        tone: 'primary' },
};

const TONE_CLASSES = {
  emerald: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
  amber:   'border-amber-400/30 bg-amber-400/10 text-amber-300',
  primary: 'border-primary/30 bg-primary/10 text-primary',
  secondary: 'border-secondary/30 bg-secondary/10 text-secondary',
  muted:   'border-white/10 bg-white/[0.03] text-muted-foreground',
};

export default function NotificationsPage() {
  const [events, setEvents] = useState(null);

  useEffect(() => {
    activityService.list(40).then(setEvents).catch((e) => {
      toast.error(formatApiError(e));
      setEvents([]);
    });
  }, []);

  if (!events) {
    return (
      <div className="py-24 flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="overline">Loading activity</span>
      </div>
    );
  }

  const unread = events.filter((e) => ['mission_generated', 'mission_completed', 'task_completed'].includes(e.kind)).length;

  return (
    <div className="space-y-6" data-testid="notifications-page-root">
      <div>
        <div className="overline mb-2">Notifications</div>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">Notification Center</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          Mission updates, revision reminders and system events land here.
        </p>
      </div>

      <GlassCard className="p-2 sm:p-3">
        {events.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            No notifications yet — start today's mission.
          </div>
        ) : (
          <div className="divide-y divide-white/[0.06]">
            {events.slice(0, 10).map((n) => {
              const meta = KIND_META[n.kind] || { icon: Bell, tone: 'muted' };
              const Icon = meta.icon;
              return (
                <div key={n.id} className="flex items-start gap-4 p-4 hover:bg-white/[0.02] transition-colors">
                  <span className={cn('h-9 w-9 rounded-lg flex items-center justify-center border shrink-0', TONE_CLASSES[meta.tone])}>
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{n.title}</p>
                    {n.description && <p className="mt-0.5 text-sm text-muted-foreground">{n.description}</p>}
                  </div>
                  <span className="text-[11px] text-muted-foreground font-mono whitespace-nowrap">
                    {formatDistanceToNow(parseISO(n.ts), { addSuffix: true })}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </GlassCard>

      <GlassCard className="p-6">
        <div className="flex items-center gap-2.5 mb-4">
          <Bell className="h-4 w-4 text-primary" />
          <div className="overline">Activity Timeline</div>
          <span className="ml-auto text-[11px] font-mono text-muted-foreground uppercase tracking-wider">
            {unread} recent
          </span>
        </div>
        {events.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing to show yet.</p>
        ) : (
          <div className="relative pl-6">
            <span className="absolute left-2 top-1 bottom-1 w-px bg-white/10" />
            {events.slice(0, 20).map((n) => (
              <div key={n.id} className="relative py-3">
                <span className="absolute -left-[22px] top-4 h-3 w-3 rounded-full bg-primary/70 ring-4 ring-background" />
                <p className="text-sm">{n.title}</p>
                {n.description && <p className="text-xs text-muted-foreground">{n.description}</p>}
                <p className="text-[11px] text-muted-foreground font-mono mt-1">
                  {formatDistanceToNow(parseISO(n.ts), { addSuffix: true })}
                </p>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
