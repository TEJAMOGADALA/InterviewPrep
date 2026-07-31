import {
  LayoutDashboard,
  Code2,
  Network,
  BookOpen,
  Sparkles,
  BarChart3,
  Settings,
  User,
} from 'lucide-react';

// NOTE (RC1.3): "Notifications" removed from Workspace sidebar; the bell in the
// top navigation continues to open the Notification Center page. Slot reserved
// for a future module.
export const NAV_ITEMS = [
  { key: 'mission-control',   label: 'Mission Control',   path: '/app/mission-control', icon: LayoutDashboard },
  { key: 'coding-arena',      label: 'Coding Arena',      path: '/app/coding-arena',    icon: Code2 },
  { key: 'system-design',     label: 'System Design',     path: '/app/system-design',   icon: Network },
  { key: 'knowledge-base',    label: 'Knowledge Base',    path: '/app/knowledge-base',  icon: BookOpen },
  { key: 'ai-mentor',         label: 'AI Mentor',         path: '/app/ai-mentor',       icon: Sparkles },
  { key: 'command-analytics', label: 'Command Analytics', path: '/app/analytics',       icon: BarChart3 },
  { key: 'settings',          label: 'Settings',          path: '/app/settings',        icon: Settings },
  { key: 'profile',           label: 'Profile',           path: '/app/profile',         icon: User },
];
