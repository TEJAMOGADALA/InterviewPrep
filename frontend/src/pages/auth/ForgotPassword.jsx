import { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { authService } from '@/services/auth.service';
import { formatApiError } from '@/utils/formatApiError';
import { FORGOT_PASSWORD } from '@/constants/testIds';
import { Loader2 } from 'lucide-react';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await authService.forgotPassword(email);
      setSent(true);
      toast.success('If the email exists, a reset link was sent.');
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Reset your password"
      subtitle="We'll email you a secure link to set a new password."
      footer={<><Link to="/login" className="text-primary hover:underline underline-offset-4">Back to sign in</Link></>}
    >
      {sent ? (
        <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm">
          If <span className="text-foreground font-medium">{email}</span> matches an account, a reset link is on the way. Please check your inbox and spam.
        </div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">Email</Label>
            <Input
              id="email" type="email"
              data-testid={FORGOT_PASSWORD.emailInput}
              value={email} onChange={(e) => setEmail(e.target.value)} required
              className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
              placeholder="you@example.com"
            />
          </div>
          {error && (
            <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-destructive text-sm px-3 py-2">{error}</div>
          )}
          <Button
            type="submit" disabled={submitting}
            data-testid={FORGOT_PASSWORD.submitButton}
            className="w-full h-11 bg-primary hover:bg-primary/90 btn-primary-glow"
          >
            {submitting ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Sending…</> : 'Send reset link'}
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}
