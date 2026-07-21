import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingScreen } from '@/components/common/LoadingScreen';

export function ProtectedRoute({ children, requireOnboarding = true }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <LoadingScreen label="Authenticating" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;

  if (requireOnboarding && !user.onboarding_completed) {
    return <Navigate to="/onboarding" replace />;
  }
  return children;
}

export function PublicOnlyRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen label="Loading" />;
  if (user) {
    return <Navigate to={user.onboarding_completed ? '/app/mission-control' : '/onboarding'} replace />;
  }
  return children;
}
