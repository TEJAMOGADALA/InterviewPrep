import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useAuth } from '@/contexts/AuthContext';
import { userService } from '@/services/auth.service';
import { onboardingService } from '@/services/mission.service';
import { TARGET_COMPANIES, POSITIONS, SELF_ASSESSMENT_TOPICS } from '@/config/companies';
import { formatApiError } from '@/utils/formatApiError';
import { PROFILE } from '@/constants/testIds';
import { Loader2, Save, Pencil, X, Check, Calendar as CalendarIcon, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'P';
}

export default function Profile() {
  const { user, refresh } = useAuth();
  const [onboarding, setOnboarding] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editingMission, setEditingMission] = useState(false);

  // Basic profile fields
  const [name, setName] = useState(user?.name || '');
  const [headline, setHeadline] = useState('');
  const [bio, setBio] = useState('');
  const [saving, setSaving] = useState(false);

  // Mission profile fields
  const [companies, setCompanies] = useState([]);
  const [position, setPosition] = useState('');
  const [hours, setHours] = useState([2]);
  const [targetDate, setTargetDate] = useState(null);
  const [savingMission, setSavingMission] = useState(false);

  useEffect(() => {
    userService.getOnboarding().then((o) => {
      setOnboarding(o);
      if (o) {
        setCompanies(o.target_companies || []);
        setPosition(o.current_position || '');
        setHours([o.daily_study_hours || 2]);
        setTargetDate(o.interview_target_date ? new Date(o.interview_target_date) : null);
      }
    }).catch(() => {});
    userService.getProfile().then((p) => {
      setName(p.name);
      setHeadline(p.headline || '');
      setBio(p.bio || '');
    });
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await userService.updateProfile({ name, headline, bio });
      await refresh();
      toast.success('Profile updated.');
      setEditing(false);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const saveMission = async () => {
    if (!companies.length) return toast.error('Pick at least one target company.');
    if (!position) return toast.error('Select your current position.');
    if (!targetDate) return toast.error('Pick a target interview date.');
    setSavingMission(true);
    try {
      const updated = await onboardingService.patch({
        target_companies: companies,
        current_position: position,
        daily_study_hours: hours[0],
        interview_target_date: targetDate.toISOString(),
      });
      setOnboarding(updated);
      toast.success('Mission profile updated. Today\'s mission will refresh.');
      setEditingMission(false);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setSavingMission(false);
    }
  };

  const toggleCompany = (id) => {
    setCompanies((cur) => cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id]);
  };

  const positionLabel = POSITIONS.find((p) => p.id === onboarding?.current_position)?.label;

  return (
    <div className="space-y-6" data-testid={PROFILE.root}>
      {/* Header card */}
      <GlassCard className="p-6 sm:p-8 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 h-56 w-56 rounded-full bg-primary/10 blur-3xl" />
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <div className="relative">
            <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary to-secondary/70 flex items-center justify-center font-display text-3xl font-semibold text-white border border-white/10">
              {initials(user?.name)}
            </div>
            <span className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-emerald-400 border-2 border-background" />
          </div>
          <div className="flex-1">
            {editing ? (
              <div className="space-y-3">
                <div>
                  <Label className="mb-1 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Name</Label>
                  <Input value={name} onChange={(e) => setName(e.target.value)} className="bg-white/[0.03] border-white/10" />
                </div>
                <div>
                  <Label className="mb-1 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Headline</Label>
                  <Input value={headline} onChange={(e) => setHeadline(e.target.value)} placeholder="Aspiring SDE-2 · Google · System Design" className="bg-white/[0.03] border-white/10" />
                </div>
                <div>
                  <Label className="mb-1 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Bio</Label>
                  <Textarea value={bio} onChange={(e) => setBio(e.target.value)} rows={3} placeholder="Tell your interviewer story in 2 lines." className="bg-white/[0.03] border-white/10" />
                </div>
              </div>
            ) : (
              <>
                <h1 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight">{user?.name}</h1>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
                {headline && <p className="mt-3 text-sm">{headline}</p>}
                {bio && <p className="mt-1 text-sm text-muted-foreground">{bio}</p>}
                <div className="mt-4 flex flex-wrap gap-2 text-[11px] font-mono uppercase tracking-wider">
                  <span className="rounded-full border border-white/10 bg-white/[0.02] px-2.5 py-1 text-muted-foreground">
                    Role · {user?.role}
                  </span>
                  {positionLabel && (
                    <span className="rounded-full border border-primary/30 bg-primary/10 px-2.5 py-1 text-primary">
                      {positionLabel}
                    </span>
                  )}
                  {user?.created_at && (
                    <span className="rounded-full border border-white/10 bg-white/[0.02] px-2.5 py-1 text-muted-foreground">
                      Joined {format(new Date(user.created_at), 'PP')}
                    </span>
                  )}
                </div>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {editing ? (
              <>
                <Button variant="ghost" onClick={() => setEditing(false)} className="text-muted-foreground">
                  <X className="h-4 w-4 mr-1.5" />Cancel
                </Button>
                <Button onClick={save} disabled={saving} className="bg-primary hover:bg-primary/90 btn-primary-glow">
                  {saving ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Saving…</> : <><Save className="h-4 w-4 mr-2" />Save</>}
                </Button>
              </>
            ) : (
              <Button
                variant="outline"
                onClick={() => setEditing(true)}
                data-testid={PROFILE.editButton}
                className="border-white/10 bg-white/[0.03] hover:bg-white/[0.06]"
              >
                <Pencil className="h-3.5 w-3.5 mr-2" /> Edit
              </Button>
            )}
          </div>
        </div>
      </GlassCard>

      {/* Mission profile — editable, drives Mission Engine */}
      <GlassCard className="p-6">
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <span className="h-8 w-8 rounded-lg border border-primary/30 bg-primary/10 flex items-center justify-center">
              <Target className="h-4 w-4 text-primary" />
            </span>
            <div>
              <h3 className="font-display text-base font-medium">Mission profile</h3>
              <p className="text-xs text-muted-foreground">Drives your daily mission and readiness score.</p>
            </div>
          </div>
          {editingMission ? (
            <div className="flex items-center gap-2">
              <Button variant="ghost" onClick={() => setEditingMission(false)} className="text-muted-foreground">
                <X className="h-4 w-4 mr-1.5" />Cancel
              </Button>
              <Button
                onClick={saveMission} disabled={savingMission}
                data-testid="profile-mission-save-button"
                className="bg-primary hover:bg-primary/90 btn-primary-glow"
              >
                {savingMission ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Saving…</> : <><Save className="h-4 w-4 mr-2" />Save</>}
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              onClick={() => setEditingMission(true)}
              data-testid="profile-mission-edit-button"
              className="border-white/10 bg-white/[0.03] hover:bg-white/[0.06]"
            >
              <Pencil className="h-3.5 w-3.5 mr-2" />Edit
            </Button>
          )}
        </div>

        {editingMission ? (
          <div className="space-y-6">
            {/* Companies */}
            <div>
              <Label className="mb-2 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Target companies</Label>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                {TARGET_COMPANIES.map((c) => {
                  const active = companies.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      onClick={() => toggleCompany(c.id)}
                      data-testid={`profile-company-${c.id}`}
                      className={cn(
                        'relative rounded-xl border px-3 py-2.5 text-left transition-colors',
                        active ? 'border-primary/50 bg-primary/10' : 'border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]',
                      )}
                    >
                      <div className="flex items-center gap-2.5">
                        <span
                          className="h-7 w-7 rounded-md border border-white/10 flex items-center justify-center font-mono text-xs"
                          style={{ background: `${c.accent}20`, color: c.accent === '#000000' ? '#fff' : c.accent }}
                        >
                          {c.name[0]}
                        </span>
                        <span className="text-sm">{c.name}</span>
                      </div>
                      {active && (
                        <span className="absolute top-1.5 right-1.5 h-4 w-4 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                          <Check className="h-2.5 w-2.5" />
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Position */}
            <div>
              <Label className="mb-2 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Current position</Label>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {POSITIONS.map((p) => {
                  const active = position === p.id;
                  return (
                    <button
                      key={p.id}
                      onClick={() => setPosition(p.id)}
                      data-testid={`profile-position-${p.id}`}
                      className={cn(
                        'rounded-lg border px-3 py-2 text-sm transition-colors',
                        active ? 'border-primary/50 bg-primary/10' : 'border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]',
                      )}
                    >
                      {p.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Study hours */}
              <div>
                <Label className="mb-2 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Daily study hours</Label>
                <div className="flex items-baseline justify-between mb-2">
                  <span className="font-display text-3xl font-semibold">
                    {hours[0]}<span className="text-base text-muted-foreground">h</span>
                  </span>
                  <span className="text-xs text-muted-foreground">1h – 8h</span>
                </div>
                <Slider
                  value={hours} onValueChange={setHours}
                  min={1} max={8} step={0.5}
                  data-testid="profile-hours-slider"
                />
              </div>

              {/* Target date */}
              <div>
                <Label className="mb-2 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Target interview date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <button
                      data-testid="profile-target-date"
                      className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04] transition-colors text-left"
                    >
                      <CalendarIcon className="h-4 w-4 text-primary" />
                      <span className="text-sm">
                        {targetDate ? format(targetDate, 'PPP') : 'Select date'}
                      </span>
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="p-0 bg-[hsl(var(--surface))]/95 border-white/10 backdrop-blur-xl">
                    <Calendar
                      mode="single"
                      selected={targetDate}
                      onSelect={setTargetDate}
                      initialFocus
                      disabled={(d) => d < new Date()}
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="lg:col-span-2">
              <div className="overline mb-2">Target companies</div>
              {onboarding?.target_companies?.length ? (
                <div className="flex flex-wrap gap-2">
                  {onboarding.target_companies.map((id) => {
                    const c = TARGET_COMPANIES.find((x) => x.id === id);
                    if (!c) return null;
                    return (
                      <span
                        key={id}
                        className="rounded-lg border border-white/10 bg-white/[0.03] px-2.5 py-1.5 text-sm flex items-center gap-2"
                      >
                        <span
                          className="h-5 w-5 rounded-md flex items-center justify-center font-mono text-[10px] border border-white/10"
                          style={{ background: `${c.accent}25`, color: c.accent === '#000000' ? '#fff' : c.accent }}
                        >
                          {c.name[0]}
                        </span>
                        {c.name}
                      </span>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Not set.</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="overline mb-1">Target date</div>
                <p className="text-sm font-medium">
                  {onboarding?.interview_target_date ? format(new Date(onboarding.interview_target_date), 'PP') : '—'}
                </p>
              </div>
              <div>
                <div className="overline mb-1">Study hours</div>
                <p className="text-sm font-medium">{onboarding?.daily_study_hours ?? '—'} h / day</p>
              </div>
              <div>
                <div className="overline mb-1">Experience</div>
                <p className="text-sm font-medium">{positionLabel || '—'}</p>
              </div>
              <div>
                <div className="overline mb-1">Prep estimate</div>
                <p className="text-sm font-medium">{onboarding?.estimated_prep_days ?? '—'} days</p>
              </div>
            </div>
          </div>
        )}
      </GlassCard>

      {/* Skills */}
      <GlassCard className="p-6">
        <div className="overline mb-4">Skill baseline · auto-updates from missions</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {SELF_ASSESSMENT_TOPICS.map((t) => {
            const v = onboarding?.self_assessment?.[t.key] ?? 0;
            return (
              <div key={t.key}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-sm">{t.label}</span>
                  <span className="font-mono text-xs text-primary">{v}/10</span>
                </div>
                <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                  <div className="h-full bg-primary/80" style={{ width: `${v * 10}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
}
