import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { authService } from '@/services/auth.service';
import { formatApiError } from '@/utils/formatApiError';
import { RESET_PASSWORD } from '@/constants/testIds';
import { Loader2 } from 'lucide-react';

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get('token') || '';
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) return setError('Password must be at least 8 characters.');
    if (password !== confirm) return setError('Passwords do not match.');
    if (!token) return setError('Reset token missing from URL.');
    setSubmitting(true);
    try {
      await authService.resetPassword(token, password);
      toast.success('Password updated. Please sign in.');
      navigate('/login', { replace: true });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Set a new password"
      subtitle="Choose something you can remember."
      footer={<><Link to="/login" className="text-primary hover:underline underline-offset-4">Back to sign in</Link></>}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="pwd" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">New password</Label>
          <Input
            id="pwd" type="password"
            data-testid={RESET_PASSWORD.passwordInput}
            value={password} onChange={(e) => setPassword(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="At least 8 characters"
          />
        </div>
        <div>
          <Label htmlFor="conf" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Confirm password</Label>
          <Input
            id="conf" type="password"
            data-testid={RESET_PASSWORD.confirmInput}
            value={confirm} onChange={(e) => setConfirm(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="Repeat password"
          />
        </div>
        {error && (
          <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-destructive text-sm px-3 py-2">{error}</div>
        )}
        <Button
          type="submit" disabled={submitting}
          data-testid={RESET_PASSWORD.submitButton}
          className="w-full h-11 bg-primary hover:bg-primary/90 btn-primary-glow"
        >
          {submitting ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Updating…</> : 'Update password'}
        </Button>
      </form>
    </AuthLayout>
  );
}
