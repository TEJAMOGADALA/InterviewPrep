import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { formatApiError } from '@/utils/formatApiError';
import { REGISTER } from '@/constants/testIds';
import { Loader2 } from 'lucide-react';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) return setError('Password must be at least 8 characters.');
    if (password !== confirm) return setError('Passwords do not match.');
    setSubmitting(true);
    try {
      const user = await register(name, email, password);
      toast.success(`Welcome, ${user.name.split(' ')[0]}. Let's initialize your mission.`);
      navigate('/onboarding', { replace: true });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Create your PrepOS account"
      subtitle="Your AI Interview Operating System — for Product-Based Companies."
      footer={
        <>
          Already have an account?{' '}
          <Link
            to="/login"
            data-testid={REGISTER.loginLink}
            className="text-primary hover:underline underline-offset-4"
          >
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Full name</Label>
          <Input
            id="name" data-testid={REGISTER.nameInput}
            value={name} onChange={(e) => setName(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="Ada Lovelace"
          />
        </div>
        <div>
          <Label htmlFor="email" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Email</Label>
          <Input
            id="email" type="email" autoComplete="email"
            data-testid={REGISTER.emailInput}
            value={email} onChange={(e) => setEmail(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <Label htmlFor="password" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Password</Label>
          <Input
            id="password" type="password" autoComplete="new-password"
            data-testid={REGISTER.passwordInput}
            value={password} onChange={(e) => setPassword(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="At least 8 characters"
          />
        </div>
        <div>
          <Label htmlFor="confirm" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Confirm password</Label>
          <Input
            id="confirm" type="password" autoComplete="new-password"
            data-testid={REGISTER.passwordConfirmInput}
            value={confirm} onChange={(e) => setConfirm(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="Repeat password"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-destructive text-sm px-3 py-2">
            {error}
          </div>
        )}

        <Button
          type="submit" disabled={submitting}
          data-testid={REGISTER.submitButton}
          className="w-full h-11 bg-primary hover:bg-primary/90 btn-primary-glow"
        >
          {submitting ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Creating account…</> : 'Create account'}
        </Button>
      </form>
    </AuthLayout>
  );
}
