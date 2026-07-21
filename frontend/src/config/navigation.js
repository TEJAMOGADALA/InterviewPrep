import {
  LayoutDashboard,
  Code2,
  Network,
  BookOpen,
  Sparkles,
  BarChart3,
  Bell,
  Settings,
  User,
} from 'lucide-react';

export const NAV_ITEMS = [
  { key: 'mission-control', label: 'Mission Control', path: '/app/mission-control', icon: LayoutDashboard },
  { key: 'coding-arena', label: 'Coding Arena', path: '/app/coding-arena', icon: Code2 },
  { key: 'system-design', label: 'System Design', path: '/app/system-design', icon: Network },
  { key: 'knowledge-base', label: 'Knowledge Base', path: '/app/knowledge-base', icon: BookOpen },
  { key: 'ai-mentor', label: 'AI Mentor', path: '/app/ai-mentor', icon: Sparkles },
  { key: 'command-analytics', label: 'Command Analytics', path: '/app/analytics', icon: BarChart3 },
  { key: 'notifications', label: 'Notifications', path: '/app/notifications', icon: Bell },
  { key: 'settings', label: 'Settings', path: '/app/settings', icon: Settings },
  { key: 'profile', label: 'Profile', path: '/app/profile', icon: User },
];
