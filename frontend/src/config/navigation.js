import {
  LayoutDashboard,
  Code2,
  Network,
  BookOpen,
  Sparkles,
  BarChart3,
  Settings,
} from 'lucide-react';

// NOTE (RC1.3 / RC1.3.1):
//   • "Notifications" removed — bell in top navigation opens the same page.
//   • "Profile" removed — the sidebar user block (bottom-left) and topbar
//     avatar are the two canonical entry points to the profile. Route
//     `/app/profile` is preserved so all deep-links continue to work.
//   Both slots reserved for future modules.
export const NAV_ITEMS = [
  { key: 'mission-control',   label: 'Mission Control',   path: '/app/mission-control', icon: LayoutDashboard },
  { key: 'coding-arena',      label: 'Coding Arena',      path: '/app/coding-arena',    icon: Code2 },
  { key: 'system-design',     label: 'System Design',     path: '/app/system-design',   icon: Network },
  { key: 'knowledge-base',    label: 'Knowledge Base',    path: '/app/knowledge-base',  icon: BookOpen },
  { key: 'ai-mentor',         label: 'AI Mentor',         path: '/app/ai-mentor',       icon: Sparkles },
  { key: 'command-analytics', label: 'Command Analytics', path: '/app/analytics',       icon: BarChart3 },
  { key: 'settings',          label: 'Settings',          path: '/app/settings',        icon: Settings },
];
