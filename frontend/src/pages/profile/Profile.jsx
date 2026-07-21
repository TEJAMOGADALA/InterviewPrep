import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { GlassCard } from '@/components/common/GlassCard';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';
import { userService } from '@/services/auth.service';
import { TARGET_COMPANIES, POSITIONS, SELF_ASSESSMENT_TOPICS } from '@/config/companies';
import { formatApiError } from '@/utils/formatApiError';
import { PROFILE } from '@/constants/testIds';
import { Loader2, Save, Pencil, X } from 'lucide-react';

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'P';
}

export default function Profile() {
  const { user, refresh } = useAuth();
  const [onboarding, setOnboarding] = useState(null);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [headline, setHeadline] = useState('');
  const [bio, setBio] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    userService.getOnboarding().then(setOnboarding).catch(() => {});
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

      {/* Mission overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <GlassCard className="p-6 lg:col-span-2">
          <div className="overline mb-3">Target companies</div>
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
        </GlassCard>

        <GlassCard className="p-6">
          <div className="overline mb-3">Target date</div>
          <p className="font-display text-2xl font-semibold tracking-tight">
            {onboarding?.interview_target_date
              ? format(new Date(onboarding.interview_target_date), 'PPP')
              : '—'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Estimated prep · {onboarding?.estimated_prep_days ?? '—'} days
          </p>
        </GlassCard>
      </div>

      {/* Skills */}
      <GlassCard className="p-6">
        <div className="overline mb-4">Skill baseline</div>
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
