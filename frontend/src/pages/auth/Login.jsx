import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { formatApiError } from '@/utils/formatApiError';
import { LOGIN } from '@/constants/testIds';
import { Loader2 } from 'lucide-react';

export default function Login() {
  const { login, resendVerification } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [sendingVerification, setSendingVerification] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);

  const from = location.state?.from?.pathname || null;

  // New: Show banner after successful registration
  const registeredEmail = location.state?.registeredEmail;
  const verified = new URLSearchParams(location.search).get("verified");

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.name.split(' ')[0]}`);
      if (from) navigate(from, { replace: true });
      else if (!user.onboarding_completed) navigate('/onboarding', { replace: true });
      else navigate('/app/mission-control', { replace: true });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleResendVerification = async () => {
    if (!email.trim()) {
      toast.error("Please enter your email address.");
      return;
    }

    try {
      setSendingVerification(true);

      const result = await resendVerification(email);

      toast.success(result.message);

      setVerificationSent(true);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setSendingVerification(false);
    }
  };

  return (
    <AuthLayout
      title="Sign in to PrepOS"
      subtitle="Continue your mission."
      footer={
        <>
          Don't have an account?{' '}
          <Link
            to="/register"
            data-testid={LOGIN.registerLink}
            className="text-primary hover:underline underline-offset-4"
          >
            Create one
          </Link>
        </>
      }
    >

      {verified === "true" && (
        <div className="mb-4 rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm">
          <p className="font-medium text-green-400">
            ✅ Email verified successfully!
          </p>

          <p className="mt-1 text-muted-foreground">
            Your PrepOS account has been verified.
            You can now sign in.
          </p>
        </div>
      )}

      {registeredEmail && (
        <div className="mb-4 rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm">
          <p className="font-medium text-primary">
            Registration successful!
          </p>

          <p className="mt-1 text-muted-foreground">
            We've sent a verification email to{' '}
            <span className="font-medium text-foreground">
              {registeredEmail}
            </span>.
            <br />
            Please verify your email before signing in.
          </p>
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="email" className="mb-1.5 block text-xs font-mono uppercase tracking-wider text-muted-foreground">
            Email
          </Label>
          <Input
            id="email" type="email" autoComplete="email"
            data-testid={LOGIN.emailInput}
            value={email} onChange={(e) => setEmail(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <Label htmlFor="password" className="text-xs font-mono uppercase tracking-wider text-muted-foreground">
              Password
            </Label>
            <Link
              to="/forgot-password"
              data-testid={LOGIN.forgotPasswordLink}
              className="text-xs text-primary hover:underline underline-offset-4"
            >
              Forgot password?
            </Link>
          </div>
          <Input
            id="password" type="password" autoComplete="current-password"
            data-testid={LOGIN.passwordInput}
            value={password} onChange={(e) => setPassword(e.target.value)} required
            className="bg-white/[0.03] border-white/10 focus-visible:ring-primary"
            placeholder="••••••••"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-sm px-3 py-2">

            <p className="text-destructive">
              {error}
            </p>

            {error.includes("not been verified") && (
              <div className="mt-3">

                <p className="text-xs text-muted-foreground">
                  Didn't receive the email?
                </p>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  disabled={sendingVerification || verificationSent}
                  onClick={handleResendVerification}
                >
                  {sendingVerification
                    ? "Sending..."
                    : "Resend Verification Email"}
                </Button>

                {verificationSent && (
                  <p className="mt-2 text-sm text-green-500">
                    ✅ Verification email sent.
                    <br />
                    Please check your inbox.
                  </p>
                )}

              </div>
            )}

          </div>
        )}

        <Button
          type="submit"
          disabled={submitting}
          data-testid={LOGIN.submitButton}
          className="w-full h-11 bg-primary hover:bg-primary/90 btn-primary-glow"
        >
          {submitting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Signing in…
            </>
          ) : (
            'Sign in'
          )}
        </Button>
      </form>
    </AuthLayout>
  );
}
