import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import '@/App.css';

import { AuthProvider } from '@/contexts/AuthContext';
import { ProtectedRoute, PublicOnlyRoute } from '@/components/ProtectedRoute';
import { AppShell } from '@/components/layout/AppShell';

import RootRedirect from '@/pages/RootRedirect';
import Login from '@/pages/auth/Login';
import Register from '@/pages/auth/Register';
import ForgotPassword from '@/pages/auth/ForgotPassword';
import ResetPassword from '@/pages/auth/ResetPassword';
import MissionInit from '@/pages/onboarding/MissionInit';
import MissionControl from '@/pages/dashboard/MissionControl';
import CodingArena from '@/pages/coding/CodingArena';
import SystemDesign from '@/pages/system-design/SystemDesign';
import KnowledgeBase from '@/pages/knowledge/KnowledgeBase';
import DeepTopicPage from '@/pages/knowledge/DeepTopicPage';
import AIMentor from '@/pages/ai-mentor/AIMentor';
import CommandAnalytics from '@/pages/analytics/CommandAnalytics';
import NotificationsPage from '@/pages/notifications/NotificationsPage';
import Settings from '@/pages/settings/Settings';
import Profile from '@/pages/profile/Profile';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
            <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
            <Route path="/forgot-password" element={<PublicOnlyRoute><ForgotPassword /></PublicOnlyRoute>} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Onboarding (auth required, but no onboarding requirement) */}
            <Route
              path="/onboarding"
              element={
                <ProtectedRoute requireOnboarding={false}>
                  <MissionInit />
                </ProtectedRoute>
              }
            />

            {/* App shell (auth + onboarding required) */}
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <AppShell />
                </ProtectedRoute>
              }
            >
              <Route path="mission-control" element={<MissionControl />} />
              <Route path="coding-arena" element={<CodingArena />} />
              <Route path="system-design" element={<SystemDesign />} />
              <Route path="knowledge-base" element={<KnowledgeBase />} />
              <Route path="knowledge-base/nodes/:nodeId" element={<DeepTopicPage />} />
              <Route path="ai-mentor" element={<AIMentor />} />
              <Route path="analytics" element={<CommandAnalytics />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="settings" element={<Settings />} />
              <Route path="profile" element={<Profile />} />
            </Route>

            {/* Root */}
            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<RootRedirect />} />
          </Routes>
        </AuthProvider>
        <Toaster theme="dark" richColors position="bottom-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;
