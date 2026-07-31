import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { GlassCard } from '@/components/common/GlassCard';
import { userService } from '@/services/auth.service';
import { useAuth } from '@/contexts/AuthContext';
import { TARGET_COMPANIES } from '@/config/companies';
import { formatApiError } from '@/utils/formatApiError';
import { SETTINGS } from '@/constants/testIds';
import { Loader2, Save, KeyRound, Sun, Moon, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/contexts/ThemeContext';

const AI_PROVIDERS = [
  {
    id: 'gemini',
    label: 'Google Gemini',
    active: true,
    model: 'gemini-flash-latest',
    tagline: 'Fast · high free tier · recommended',
    accent: 'from-sky-500/70 to-blue-500/60',
    initials: 'G',
    keyLabel: 'Gemini API Key',
    keyHint: 'Get one at aistudio.google.com/apikey',
  },
  {
    id: 'openai',
    label: 'OpenAI',
    active: false,
    model: 'gpt-5.2',
    tagline: 'Frontier quality · pay-as-you-go',
    accent: 'from-emerald-500/70 to-teal-500/60',
    initials: 'O',
    keyLabel: 'OpenAI API Key',
    keyHint: 'platform.openai.com/api-keys',
  },
  {
    id: 'claude',
    label: 'Anthropic Claude',
    active: false,
    model: 'claude-sonnet-4.5',
    tagline: 'Strong reasoning · long context',
    accent: 'from-orange-500/70 to-amber-500/60',
    initials: 'A',
    keyLabel: 'Anthropic API Key',
    keyHint: 'console.anthropic.com/settings/keys',
  },
  {
    id: 'deepseek',
    label: 'DeepSeek',
    active: false,
    model: 'deepseek-chat',
    tagline: 'Cost-effective · open weights',
    accent: 'from-violet-500/70 to-fuchsia-500/60',
    initials: 'D',
    keyLabel: 'DeepSeek API Key',
    keyHint: 'platform.deepseek.com',
  },
];

// Curated list of Gemini models with rich metadata for the redesigned picker.
const GEMINI_MODELS = [
  { id: 'gemini-flash-latest',   label: 'gemini-flash-latest',   tagline: 'Recommended · always the latest Flash',       badge: 'Recommended', quality: 'Balanced', speed: 'Fast',    cost: 'Free tier friendly' },
  { id: 'gemini-pro-latest',     label: 'gemini-pro-latest',     tagline: 'Higher quality · slower · more quota',         badge: 'Higher quality', quality: 'Premium', speed: 'Slower', cost: 'More quota' },
  { id: 'gemini-flash-lite-latest', label: 'gemini-flash-lite-latest', tagline: 'Cheapest · fastest',                     badge: 'Cheapest', quality: 'Standard', speed: 'Fastest', cost: 'Lowest' },
  { id: 'gemini-3.6-flash',      label: 'gemini-3.6-flash',      tagline: 'Pinned latest-gen Flash',                       badge: 'Pinned', quality: 'Balanced', speed: 'Fast',    cost: 'Free tier friendly' },
  { id: 'gemini-3.5-flash',      label: 'gemini-3.5-flash',      tagline: 'Pinned Gemini 3.5 Flash',                       badge: 'Pinned', quality: 'Balanced', speed: 'Fast',    cost: 'Free tier friendly' },
  { id: 'gemini-2.0-flash',      label: 'gemini-2.0-flash',      tagline: 'Older Flash · lower free-tier quota',           badge: 'Legacy',   quality: 'Standard', speed: 'Fast',    cost: 'Limited quota' },
];

export default function Settings() {
  const { user, refresh } = useAuth();
  const { theme: activeTheme, setTheme } = useTheme();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState(null);
  const [onboarding, setOnboarding] = useState(null);
  const [name, setName] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [s, o] = await Promise.all([
          userService.getSettings(),
          userService.getOnboarding(),
        ]);
        setSettings(s);
        setOnboarding(o);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => { if (user) setName(user.name); }, [user]);

  if (loading || !settings) {
    return <div className="py-20 text-center text-muted-foreground">Loading…</div>;
  }

  const patch = (partial) => setSettings((s) => ({ ...s, ...partial }));
  const patchAI = (partial) => setSettings((s) => ({ ...s, ai_config: { ...s.ai_config, ...partial } }));
  const patchNotif = (partial) => setSettings((s) => ({ ...s, notification_prefs: { ...s.notification_prefs, ...partial } }));

  const save = async () => {
    setSaving(true);
    try {
      if (name && name !== user.name) {
        await userService.updateProfile({ name });
        await refresh();
      }
      const updated = await userService.updateSettings({
        theme: settings.theme,
        ai_config: settings.ai_config,
        notification_prefs: settings.notification_prefs,
      });
      setSettings(updated);
      toast.success('Settings saved.');
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6" data-testid={SETTINGS.root}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="overline mb-2">Settings</div>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">
            Workspace preferences
          </h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
            Tune your workspace, your target companies, and how PrepOS collaborates with your AI.
          </p>
        </div>
        <Button
          onClick={save}
          disabled={saving}
          data-testid={SETTINGS.saveButton}
          className="h-10 bg-primary hover:bg-primary/90 btn-primary-glow"
        >
          {saving ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Saving…</> : <><Save className="h-4 w-4 mr-2" />Save changes</>}
        </Button>
      </div>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="bg-[hsl(var(--surface))]/60 border border-white/[0.06] rounded-xl p-1 flex w-full flex-wrap h-auto">
          <TabsTrigger value="profile" data-testid={SETTINGS.tabProfile} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">Profile</TabsTrigger>
          <TabsTrigger value="theme" data-testid={SETTINGS.tabTheme} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">Theme</TabsTrigger>
          <TabsTrigger value="study" data-testid={SETTINGS.tabStudy} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">Study hours</TabsTrigger>
          <TabsTrigger value="companies" data-testid={SETTINGS.tabCompanies} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">Target Companies</TabsTrigger>
          <TabsTrigger value="ai" data-testid={SETTINGS.tabAI} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">AI Configuration</TabsTrigger>
          <TabsTrigger value="notifications" data-testid={SETTINGS.tabNotifications} className="data-[state=active]:bg-primary/15 data-[state=active]:text-foreground rounded-lg px-4 py-2">Notifications</TabsTrigger>
        </TabsList>

        {/* Profile */}
        <TabsContent value="profile" className="mt-6">
          <GlassCard className="p-6 space-y-5 max-w-2xl">
            <div>
              <Label className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Full name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} className="bg-white/[0.03] border-white/10" />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Email</Label>
              <Input value={user.email} disabled className="bg-white/[0.02] border-white/10 opacity-70" />
              <p className="mt-1.5 text-xs text-muted-foreground">Email is used as your unique identifier — cannot be edited yet.</p>
            </div>
          </GlassCard>
        </TabsContent>

        {/* Theme */}
        <TabsContent value="theme" className="mt-6">
          <GlassCard className="p-6 max-w-2xl">
            <p className="text-sm text-muted-foreground mb-4">
              Choose how PrepOS looks. System matches your operating system preference and updates automatically.
            </p>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'light',  label: 'Light',  hint: 'Bright · calm',      icon: Sun },
                { id: 'dark',   label: 'Dark',   hint: 'Default · premium', icon: Moon },
                { id: 'system', label: 'System', hint: 'Follows OS',        icon: Monitor },
              ].map((t) => {
                const active = activeTheme === t.id;
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    onClick={() => { setTheme(t.id); patch({ theme: t.id }); }}
                    data-testid={`settings-theme-${t.id}`}
                    className={cn(
                      'relative rounded-xl border p-4 text-left transition-all',
                      active
                        ? 'border-primary/50 bg-primary/10 shadow-[0_0_0_1px_hsl(var(--primary)/0.3)]'
                        : 'hairline bg-foreground/[0.02] hover:bg-foreground/[0.04]',
                    )}
                  >
                    <Icon className={cn('h-4 w-4 mb-2', active ? 'text-primary' : 'text-muted-foreground')} />
                    <div className="capitalize font-medium">{t.label}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">{t.hint}</div>
                  </button>
                );
              })}
            </div>
          </GlassCard>
        </TabsContent>

        {/* Study hours */}
        <TabsContent value="study" className="mt-6">
          <GlassCard className="p-6 max-w-2xl">
            <div className="overline mb-2">Current baseline (from onboarding)</div>
            <div className="flex items-baseline gap-2 mb-6">
              <span className="font-display text-4xl font-semibold">
                {onboarding?.daily_study_hours ?? '—'}
              </span>
              <span className="text-sm text-muted-foreground">hours / day</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Editing your daily study budget lives with the Mission Engine (Phase 2), so it can rebalance your plan.
            </p>
          </GlassCard>
        </TabsContent>

        {/* Companies */}
        <TabsContent value="companies" className="mt-6">
          <GlassCard className="p-6">
            <div className="overline mb-3">Your targets</div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {TARGET_COMPANIES.map((c) => {
                const active = onboarding?.target_companies?.includes(c.id);
                return (
                  <div
                    key={c.id}
                    className={cn(
                      'rounded-xl border px-3 py-3 flex items-center gap-2.5',
                      active ? 'border-primary/40 bg-primary/10' : 'border-white/[0.06] bg-white/[0.02] opacity-70',
                    )}
                  >
                    <span
                      className="h-7 w-7 rounded-md border border-white/10 flex items-center justify-center font-mono text-xs"
                      style={{ background: `${c.accent}20`, color: c.accent === '#000000' ? '#fff' : c.accent }}
                    >
                      {c.name[0]}
                    </span>
                    <span className="text-sm">{c.name}</span>
                  </div>
                );
              })}
            </div>
            <p className="mt-4 text-xs text-muted-foreground">
              Editing targets rebalances your mission plan and ships with the Mission Engine.
            </p>
          </GlassCard>
        </TabsContent>

        {/* AI Configuration */}
        <TabsContent value="ai" className="mt-6">
          <GlassCard className="p-6 space-y-6 max-w-3xl">
            {/* Provider selector — visual card grid */}
            <div>
              <div className="flex items-baseline justify-between mb-3">
                <Label className="text-xs font-mono uppercase tracking-wider text-muted-foreground">AI Provider</Label>
                <span className="text-[10px] font-mono text-muted-foreground">Choose the engine powering AI Mentor & Knowledge Base</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {AI_PROVIDERS.map((p) => {
                  const active = settings.ai_config.provider === p.id;
                  return (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => {
                        patchAI({
                          provider: p.id,
                          // Keep the current model when switching between providers if
                          // it belongs to the newly selected one; otherwise reset to
                          // that provider's default so the UI stays coherent.
                          model_name: p.active ? (settings.ai_config.model_name && p.id === 'gemini' ? settings.ai_config.model_name : p.model) : p.model,
                        });
                      }}
                      data-testid={`${SETTINGS.aiProviderSelect}-${p.id}`}
                      className={cn(
                        'relative text-left rounded-xl border p-4 transition-all',
                        active
                          ? 'border-primary/50 bg-primary/10 shadow-[0_0_0_1px_hsl(var(--primary)/0.3)]'
                          : 'hairline bg-foreground/[0.02] hover:bg-foreground/[0.04] hover:border-primary/25',
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <span className={cn(
                          'h-9 w-9 rounded-lg bg-gradient-to-br flex items-center justify-center text-white font-display font-semibold shrink-0 border border-foreground/10',
                          p.accent,
                        )}>
                          {p.initials}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-medium">{p.label}</span>
                            {!p.active && (
                              <span className="text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-400/10 text-amber-300 border border-amber-400/30">
                                Coming soon
                              </span>
                            )}
                            {active && (
                              <span className="ml-auto h-2 w-2 rounded-full bg-primary" />
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground mt-0.5">{p.tagline}</div>
                          <div className="mt-1.5 text-[10px] font-mono text-muted-foreground/70">
                            Default: {p.model}
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Provider-specific config */}
            {(() => {
              const selectedProvider = AI_PROVIDERS.find((x) => x.id === settings.ai_config.provider) || AI_PROVIDERS[0];
              const isActive = selectedProvider.active;
              return (
                <div className={cn('space-y-5 rounded-xl border p-5', isActive ? 'hairline bg-foreground/[0.02]' : 'border-amber-400/30 bg-amber-400/[0.05]')}>
                  {!isActive && (
                    <div className="flex items-start gap-2.5 -mt-1">
                      <span className="h-5 w-5 rounded-full bg-amber-400/20 border border-amber-400/40 flex items-center justify-center text-amber-300 text-[10px] font-mono shrink-0 mt-0.5">!</span>
                      <div className="text-xs text-amber-200/90">
                        <span className="font-medium">{selectedProvider.label}</span> integration coming soon.
                        You can pre-configure the fields below — they will activate once the provider is wired up.
                      </div>
                    </div>
                  )}

                  <div>
                    <Label className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">
                      {selectedProvider.keyLabel}
                    </Label>
                    <div className="relative">
                      <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="password"
                        placeholder={isActive ? 'Paste your API key' : 'Coming soon — key input disabled'}
                        value={settings.ai_config.api_key || ''}
                        onChange={(e) => patchAI({ api_key: e.target.value })}
                        data-testid={SETTINGS.aiKeyInput}
                        disabled={!isActive}
                        className={cn('pl-9 bg-foreground/[0.03]', !isActive && 'opacity-60 cursor-not-allowed')}
                      />
                    </div>
                    <p className="mt-1.5 text-xs text-muted-foreground">
                      {selectedProvider.keyHint} · Stored per-user, encrypted at rest.
                    </p>
                  </div>

                  <div>
                    <Label className="mb-2 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Model</Label>
                    {selectedProvider.id === 'gemini' ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {GEMINI_MODELS.map((m) => {
                          const active = settings.ai_config.model_name === m.id;
                          return (
                            <button
                              key={m.id}
                              type="button"
                              onClick={() => patchAI({ model_name: m.id })}
                              data-testid={`${SETTINGS.aiModelInput}-${m.id}`}
                              className={cn(
                                'relative text-left rounded-lg border p-3 transition-all',
                                active
                                  ? 'border-primary/50 bg-primary/10 shadow-[0_0_0_1px_hsl(var(--primary)/0.25)]'
                                  : 'hairline bg-foreground/[0.02] hover:bg-foreground/[0.04]',
                              )}
                            >
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <span className="font-mono text-[13px] truncate">{m.label}</span>
                                {m.badge && (
                                  <span className={cn(
                                    'text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border shrink-0',
                                    m.badge === 'Recommended' && 'border-primary/40 bg-primary/10 text-primary',
                                    m.badge === 'Higher quality' && 'border-emerald-400/40 bg-emerald-400/10 text-emerald-300',
                                    m.badge === 'Cheapest' && 'border-sky-400/40 bg-sky-400/10 text-sky-300',
                                    m.badge === 'Pinned' && 'border-muted-foreground/30 bg-foreground/[0.04] text-muted-foreground',
                                    m.badge === 'Legacy' && 'border-amber-400/40 bg-amber-400/10 text-amber-300',
                                  )}>
                                    {m.badge}
                                  </span>
                                )}
                              </div>
                              <div className="text-[11px] text-muted-foreground">{m.tagline}</div>
                              <div className="mt-2 flex flex-wrap gap-x-3 gap-y-0.5 text-[10px] font-mono text-muted-foreground/80">
                                <span>⚡ {m.speed}</span>
                                <span>✦ {m.quality}</span>
                                <span>$ {m.cost}</span>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="rounded-lg border hairline bg-foreground/[0.02] p-3">
                        <div className="font-mono text-[13px]">{selectedProvider.model}</div>
                        <div className="text-[11px] text-muted-foreground mt-0.5">
                          Model selection unlocks when {selectedProvider.label} is enabled.
                        </div>
                      </div>
                    )}
                    {selectedProvider.id === 'gemini' && settings.ai_config.model_name &&
                      !GEMINI_MODELS.find((m) => m.id === settings.ai_config.model_name) && (
                      <p className="mt-1.5 text-xs text-amber-400/90">
                        Your saved model <span className="font-mono">{settings.ai_config.model_name}</span> is
                        deprecated for new API keys. Pick one above and Save.
                      </p>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label className="text-xs font-mono uppercase tracking-wider text-muted-foreground">Temperature</Label>
                      <span className="font-mono text-sm text-primary">{settings.ai_config.temperature.toFixed(2)}</span>
                    </div>
                    <Slider
                      value={[settings.ai_config.temperature]}
                      onValueChange={(v) => patchAI({ temperature: v[0] })}
                      min={0} max={2} step={0.05}
                      data-testid={SETTINGS.aiTempSlider}
                      disabled={!isActive}
                    />
                    <p className="mt-1.5 text-xs text-muted-foreground">Lower = deterministic. Higher = creative.</p>
                  </div>
                </div>
              );
            })()}
          </GlassCard>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications" className="mt-6">
          <GlassCard className="p-6 space-y-4 max-w-2xl">
            {[
              { key: 'email_daily_digest',       label: 'Daily digest', hint: 'Email summary of your day, mission and next steps.' },
              { key: 'email_weekly_report',      label: 'Weekly report', hint: 'End-of-week analytics and retention checkpoints.' },
              { key: 'push_streak_reminders',    label: 'Streak reminders', hint: 'Nudge me when I might lose my streak.' },
              { key: 'push_upcoming_revisions',  label: 'Upcoming revisions', hint: 'Alerts when spaced-repetition items are due.' },
              { key: 'push_mission_updates',     label: 'Mission updates', hint: 'When missions are generated or rebalanced.' },
            ].map((row) => (
              <div key={row.key} className="flex items-start gap-4 rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex-1">
                  <p className="text-sm font-medium">{row.label}</p>
                  <p className="text-xs text-muted-foreground">{row.hint}</p>
                </div>
                <Switch
                  checked={settings.notification_prefs[row.key]}
                  onCheckedChange={(v) => patchNotif({ [row.key]: v })}
                />
              </div>
            ))}
          </GlassCard>
        </TabsContent>
      </Tabs>
    </div>
  );
}
