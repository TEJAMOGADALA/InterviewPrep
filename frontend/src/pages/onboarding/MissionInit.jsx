import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { Rocket, ArrowRight, ArrowLeft, Check, Calendar as CalendarIcon, Loader2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Logo } from '@/components/common/Logo';
import { TARGET_COMPANIES, POSITIONS, SELF_ASSESSMENT_TOPICS } from '@/config/companies';
import { userService } from '@/services/auth.service';
import { useAuth } from '@/contexts/AuthContext';
import { formatApiError } from '@/utils/formatApiError';
import { ONBOARDING } from '@/constants/testIds';
import { cn } from '@/lib/utils';

const STEPS = [
  'Welcome',
  'Destinations',
  'Position',
  'Study hours',
  'Self assessment',
  'Target date',
  'Initialize',
];

function estimatePrepDays(hours, skills) {
  const avg = Object.values(skills).reduce((a, b) => a + b, 0) / 7;
  const base = 180 - avg * 12;
  const hoursFactor = 4 / Math.max(hours, 1);
  return Math.max(30, Math.round((base * hoursFactor) / 2));
}

export default function MissionInit() {
  const { refresh } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(0);
  const [companies, setCompanies] = useState([]);
  const [position, setPosition] = useState('');
  const [hours, setHours] = useState([3]);
  const [skills, setSkills] = useState(
    Object.fromEntries(SELF_ASSESSMENT_TOPICS.map((t) => [t.key, 5])),
  );
  const [targetDate, setTargetDate] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const estimated = useMemo(
    () => estimatePrepDays(hours[0], skills),
    [hours, skills],
  );

  const toggleCompany = (id) => {
    setCompanies((cur) =>
      cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id],
    );
  };

  const canProceed = () => {
    if (step === 1) return companies.length > 0;
    if (step === 2) return !!position;
    if (step === 5) return !!targetDate;
    return true;
  };

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const back = () => setStep((s) => Math.max(s - 1, 0));

  const submit = async () => {
    setSubmitting(true);
    try {
      await userService.submitOnboarding({
        target_companies: companies,
        current_position: position,
        daily_study_hours: hours[0],
        self_assessment: skills,
        interview_target_date: targetDate.toISOString(),
      });
      await refresh();
      toast.success('Mission initialized. Welcome aboard.');
      navigate('/app/mission-control', { replace: true });
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen relative flex flex-col">
      {/* Ambient background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 grid-noise opacity-30" />
        <div className="absolute -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-[-160px] right-[-120px] h-[480px] w-[480px] rounded-full bg-secondary/10 blur-3xl" />
      </div>

      <header className="px-6 py-6 flex items-center justify-between">
        <Logo />
        <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
          Mission Initialization
        </div>
      </header>

      {/* Progress bar */}
      <div className="px-6" data-testid={ONBOARDING.stepIndicator}>
        <div className="mx-auto max-w-3xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-muted-foreground font-mono">
              Step {step + 1} of {STEPS.length}
            </span>
            <span className="text-xs text-foreground font-medium">{STEPS[step]}</span>
          </div>
          <div className="relative h-1 rounded-full bg-white/[0.05] overflow-hidden">
            <motion.div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-secondary"
              animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
              transition={{ type: 'spring', stiffness: 200, damping: 30 }}
            />
          </div>
        </div>
      </div>

      <main className="flex-1 flex items-center justify-center px-6 py-10">
        <div
          className="w-full max-w-3xl rounded-2xl border border-white/[0.08] bg-[hsl(var(--surface))]/70 backdrop-blur-xl p-8 sm:p-10"
          data-testid={ONBOARDING.wizard}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
            >
              {step === 0 && <StepWelcome onStart={next} />}
              {step === 1 && (
                <StepCompanies value={companies} onToggle={toggleCompany} />
              )}
              {step === 2 && <StepPosition value={position} onChange={setPosition} />}
              {step === 3 && (
                <StepHours value={hours} onChange={setHours} estimated={estimated} />
              )}
              {step === 4 && (
                <StepSelfAssessment values={skills} onChange={setSkills} />
              )}
              {step === 5 && (
                <StepTargetDate value={targetDate} onChange={setTargetDate} estimated={estimated} />
              )}
              {step === 6 && <StepInitialize submitting={submitting} onLaunch={submit} />}
            </motion.div>
          </AnimatePresence>

          {step > 0 && step < 6 && (
            <div className="mt-10 flex items-center justify-between">
              <Button
                variant="ghost" onClick={back}
                data-testid={ONBOARDING.backButton}
                className="text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft className="h-4 w-4 mr-1.5" /> Back
              </Button>
              <Button
                onClick={next} disabled={!canProceed()}
                data-testid={ONBOARDING.nextButton}
                className="h-11 px-6 bg-primary hover:bg-primary/90 btn-primary-glow"
              >
                Continue <ArrowRight className="h-4 w-4 ml-1.5" />
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

/* ----------------- Steps ----------------- */

function StepWelcome({ onStart }) {
  return (
    <div className="text-center py-8">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mx-auto mb-8 h-16 w-16 rounded-2xl bg-primary/15 border border-primary/30 flex items-center justify-center"
      >
        <Rocket className="h-6 w-6 text-primary" />
      </motion.div>
      <h1 className="font-display text-4xl sm:text-5xl font-semibold tracking-tight mb-4">
        Welcome to PrepOS
      </h1>
      <p className="text-base text-muted-foreground max-w-xl mx-auto leading-relaxed">
        Your AI Interview Operating System for Product-Based Company preparation. Let's initialize your mission — it'll take about a minute.
      </p>
      <Button
        onClick={onStart}
        data-testid={ONBOARDING.beginButton}
        className="mt-10 h-11 px-8 bg-primary hover:bg-primary/90 btn-primary-glow"
      >
        Begin Mission <ArrowRight className="h-4 w-4 ml-1.5" />
      </Button>
    </div>
  );
}

function StepCompanies({ value, onToggle }) {
  return (
    <div>
      <StepHeader
        overline="Step 02"
        title="Choose your destinations"
        subtitle="Which Product-Based Companies are you preparing for? Select all that apply."
      />
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-8">
        {TARGET_COMPANIES.map((c) => {
          const active = value.includes(c.id);
          return (
            <button
              key={c.id}
              onClick={() => onToggle(c.id)}
              data-testid={`${ONBOARDING.companyChip}-${c.id}`}
              className={cn(
                'group relative rounded-xl border px-4 py-3.5 text-left transition-colors',
                active
                  ? 'border-primary/50 bg-primary/10'
                  : 'border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]',
              )}
            >
              <div className="flex items-center gap-3">
                <span
                  className="h-8 w-8 rounded-lg border border-white/10 flex items-center justify-center font-mono text-xs"
                  style={{ background: `${c.accent}20`, color: c.accent === '#000000' ? '#fff' : c.accent }}
                >
                  {c.name[0]}
                </span>
                <span className="text-sm font-medium">{c.name}</span>
              </div>
              {active && (
                <span className="absolute top-2.5 right-2.5 h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                  <Check className="h-3 w-3" />
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function StepPosition({ value, onChange }) {
  return (
    <div>
      <StepHeader
        overline="Step 03"
        title="Where are you today?"
        subtitle="This helps us calibrate difficulty and expectations."
      />
      <div className="grid gap-2.5 mt-8">
        {POSITIONS.map((p) => {
          const active = value === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onChange(p.id)}
              data-testid={`${ONBOARDING.positionOption}-${p.id}`}
              className={cn(
                'flex items-center justify-between rounded-xl border px-4 py-3.5 text-left transition-colors',
                active
                  ? 'border-primary/50 bg-primary/10'
                  : 'border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04]',
              )}
            >
              <div>
                <p className="text-sm font-medium">{p.label}</p>
                <p className="text-xs text-muted-foreground">{p.hint}</p>
              </div>
              <div
                className={cn(
                  'h-5 w-5 rounded-full border flex items-center justify-center',
                  active ? 'border-primary bg-primary/20' : 'border-white/15',
                )}
              >
                {active && <span className="h-2 w-2 rounded-full bg-primary" />}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function StepHours({ value, onChange, estimated }) {
  return (
    <div>
      <StepHeader
        overline="Step 04"
        title="Daily study hours"
        subtitle="How much time can you invest each day? Be realistic — consistency beats intensity."
      />
      <div className="mt-10">
        <div className="flex items-baseline justify-between mb-4">
          <span className="font-display text-5xl font-semibold tracking-tight">
            {value[0]}<span className="text-2xl text-muted-foreground">h</span>
          </span>
          <span className="text-sm text-muted-foreground">
            Range · 1h – 8h
          </span>
        </div>
        <Slider
          value={value}
          onValueChange={onChange}
          min={1}
          max={8}
          step={0.5}
          data-testid={ONBOARDING.hoursSlider}
          className="[&_[role=slider]]:h-5 [&_[role=slider]]:w-5"
        />
        <div className="mt-8 rounded-xl border border-primary/30 bg-primary/[0.06] px-4 py-3 flex items-center justify-between">
          <div>
            <div className="overline mb-0.5">Estimated preparation</div>
            <div className="font-display text-lg font-medium">~ {estimated} days</div>
          </div>
          <div className="text-xs text-muted-foreground max-w-[220px] text-right">
            Refined once we know your target date and skill baseline.
          </div>
        </div>
      </div>
    </div>
  );
}

function StepSelfAssessment({ values, onChange }) {
  return (
    <div>
      <StepHeader
        overline="Step 05"
        title="Self assessment"
        subtitle="Rate your current confidence from 1 (starting out) to 10 (interview-ready)."
      />
      <div className="mt-8 grid gap-5">
        {SELF_ASSESSMENT_TOPICS.map((t) => (
          <div key={t.key}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm">{t.label}</span>
              <span className="font-mono text-sm text-primary">{values[t.key]}/10</span>
            </div>
            <Slider
              value={[values[t.key]]}
              onValueChange={(v) => onChange({ ...values, [t.key]: v[0] })}
              min={1} max={10} step={1}
              data-testid={`${ONBOARDING.skillSlider}-${t.key}`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

function StepTargetDate({ value, onChange, estimated }) {
  return (
    <div>
      <StepHeader
        overline="Step 06"
        title="Interview target date"
        subtitle="Pick a realistic target. We'll build your mission timeline around it."
      />
      <div className="mt-8 flex flex-col sm:flex-row gap-6 items-start">
        <Popover>
          <PopoverTrigger asChild>
            <button
              data-testid={ONBOARDING.targetDate}
              className={cn(
                'w-full sm:w-[280px] flex items-center gap-3 px-4 py-3.5 rounded-xl border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04] transition-colors text-left',
              )}
            >
              <CalendarIcon className="h-4 w-4 text-primary" />
              <span className="text-sm">
                {value ? format(value, 'PPP') : 'Select target date'}
              </span>
            </button>
          </PopoverTrigger>
          <PopoverContent className="p-0 bg-[hsl(var(--surface))]/95 border-white/10 backdrop-blur-xl">
            <Calendar
              mode="single"
              selected={value}
              onSelect={onChange}
              initialFocus
              disabled={(date) => date < new Date()}
            />
          </PopoverContent>
        </Popover>

        <div className="flex-1 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
          <div className="overline mb-1">Guidance</div>
          <p className="text-sm text-foreground/90">
            Our current estimate is <span className="text-primary font-medium">{estimated} days</span> of focused prep. Aiming a little further out gives buffer for mock interviews and revision.
          </p>
        </div>
      </div>
    </div>
  );
}

function StepInitialize({ submitting, onLaunch }) {
  const stages = [
    'Preparing Workspace',
    'Preparing AI Mentor',
    'Building Knowledge Graph',
    'Preparing Mission Control',
    'Creating Profile',
    'Generating Workspace',
  ];
  return (
    <div className="text-center py-4">
      <StepHeader
        overline="Step 07"
        title="Initialize your mission"
        subtitle="Everything is ready. Launch when you are."
        center
      />
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-lg mx-auto text-left">
        {stages.map((s, i) => (
          <motion.div
            key={s}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06 }}
            className="flex items-center gap-2.5 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2"
          >
            <span className="h-5 w-5 rounded-md bg-primary/15 border border-primary/30 flex items-center justify-center">
              <Check className="h-3 w-3 text-primary" />
            </span>
            <span className="text-sm">{s}</span>
          </motion.div>
        ))}
      </div>
      <Button
        onClick={onLaunch}
        disabled={submitting}
        data-testid={ONBOARDING.launchButton}
        className="mt-10 h-12 px-8 bg-primary hover:bg-primary/90 btn-primary-glow"
      >
        {submitting ? (
          <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Launching…</>
        ) : (
          <>Launch Mission Control <Rocket className="h-4 w-4 ml-2" /></>
        )}
      </Button>
    </div>
  );
}

function StepHeader({ overline, title, subtitle, center }) {
  return (
    <div className={center ? 'text-center' : ''}>
      <div className="overline mb-3">{overline}</div>
      <h2 className="font-display text-3xl font-semibold tracking-tight mb-2">{title}</h2>
      <p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
        {subtitle}
      </p>
    </div>
  );
}
