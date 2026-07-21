import { formatDistanceToNow } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import { Bell, Sparkles, CheckCircle2, Calendar } from 'lucide-react';

const NOTIFICATIONS = [
  {
    id: 'n1', icon: Sparkles, title: 'Welcome to PrepOS',
    body: 'Your workspace is initialized. The Mission Engine ships in Phase 2.',
    ts: new Date().toISOString(), unread: true,
  },
  {
    id: 'n2', icon: CheckCircle2, title: 'Profile complete',
    body: "You've locked your target companies and baseline skills.",
    ts: new Date(Date.now() - 60_000 * 12).toISOString(), unread: true,
  },
  {
    id: 'n3', icon: Calendar, title: 'Target date set',
    body: "We'll begin scheduling revision blocks from your target date.",
    ts: new Date(Date.now() - 3_600_000 * 4).toISOString(), unread: false,
  },
];

export default function NotificationsPage() {
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
        <div className="divide-y divide-white/[0.06]">
          {NOTIFICATIONS.map((n) => {
            const Icon = n.icon;
            return (
              <div key={n.id} className="flex items-start gap-4 p-4 hover:bg-white/[0.02] transition-colors">
                <span className={
                  'h-9 w-9 rounded-lg flex items-center justify-center border ' +
                  (n.unread
                    ? 'border-primary/30 bg-primary/10 text-primary'
                    : 'border-white/10 bg-white/[0.03] text-muted-foreground')
                }>
                  <Icon className="h-4 w-4" />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate">{n.title}</p>
                    {n.unread && <span className="h-1.5 w-1.5 rounded-full bg-primary" />}
                  </div>
                  <p className="mt-0.5 text-sm text-muted-foreground">{n.body}</p>
                </div>
                <span className="text-[11px] text-muted-foreground font-mono whitespace-nowrap">
                  {formatDistanceToNow(new Date(n.ts), { addSuffix: true })}
                </span>
              </div>
            );
          })}
        </div>
      </GlassCard>

      <GlassCard className="p-6">
        <div className="flex items-center gap-2.5 mb-2">
          <Bell className="h-4 w-4 text-primary" />
          <div className="overline">Activity Timeline</div>
        </div>
        <div className="relative pl-6">
          <span className="absolute left-2 top-1 bottom-1 w-px bg-white/10" />
          {NOTIFICATIONS.map((n, i) => (
            <div key={n.id} className="relative py-3">
              <span className="absolute -left-[22px] top-4 h-3 w-3 rounded-full bg-primary/70 ring-4 ring-background" />
              <p className="text-sm">{n.title}</p>
              <p className="text-xs text-muted-foreground">{n.body}</p>
              <p className="text-[11px] text-muted-foreground font-mono mt-1">
                {formatDistanceToNow(new Date(n.ts), { addSuffix: true })}
              </p>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
