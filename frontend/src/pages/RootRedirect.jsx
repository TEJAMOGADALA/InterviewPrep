import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingScreen } from '@/components/common/LoadingScreen';

// Root redirect. Sends the user where they should be right now.
export default function RootRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingScreen label="Booting workspace" />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.onboarding_completed) return <Navigate to="/onboarding" replace />;
  return <Navigate to="/app/mission-control" replace />;
}
