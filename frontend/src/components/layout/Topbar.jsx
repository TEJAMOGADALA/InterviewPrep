import { Bell, Search, LogOut, User as UserIcon, Settings, Flame, Menu, PanelLeftClose, PanelLeft, Moon, Sun, Monitor } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useCommandPalette } from '@/contexts/CommandPaletteContext';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { useUILayout } from '@/contexts/UILayoutContext';
import { useTheme } from '@/contexts/ThemeContext';
import { APP_SHELL, LOGOUT } from '@/constants/testIds';
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuSeparator, DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { Sparkles } from 'lucide-react';
import { dashboardService } from '@/services/mission.service';
import { UserAvatar } from '@/components/common/UserAvatar';
import { cn } from '@/lib/utils';

export function Topbar() {
  const { user, logout } = useAuth();
  const { setOpen: setCmdOpen } = useCommandPalette();
  const { toggle: toggleAIPanel } = useAIPanel();
  const { sidebarCollapsed, toggleSidebar } = useUILayout();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [streak, setStreak] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    dashboardService.get().then((d) => {
      if (!mounted) return;
      if (d?.streak?.current != null) setStreak(d.streak.current);
    }).catch(() => {});
    return () => { mounted = false; };
  }, []);

  const ThemeIcon = theme === 'system' ? Monitor : resolvedTheme === 'light' ? Sun : Moon;

  return (
    <header
      data-testid={APP_SHELL.topbar}
      className="sticky top-0 z-20 h-16 border-b bg-background/70 backdrop-blur-xl"
      style={{ borderColor: 'var(--hairline)' }}
    >
      <div className="h-full flex items-center gap-3 px-4 sm:px-6">
        {/* Desktop sidebar toggle */}
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          data-testid={APP_SHELL.sidebarToggle}
          className="hidden lg:inline-flex h-9 w-9 items-center justify-center rounded-lg border hover:bg-foreground/[0.04] transition-colors"
          style={{ borderColor: 'var(--hairline)' }}
        >
          {sidebarCollapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>

        <button
          type="button"
          onClick={() => setCmdOpen(true)}
          data-testid={APP_SHELL.globalSearch}
          className="group flex-1 max-w-xl flex items-center gap-3 px-3.5 py-2 rounded-lg border bg-foreground/[0.02] hover:bg-foreground/[0.04] transition-colors"
          style={{ borderColor: 'var(--hairline)' }}
        >
          <Search className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground hidden sm:inline">Search commands, missions, topics…</span>
          <span className="text-sm text-muted-foreground sm:hidden">Search…</span>
          <span className="ml-auto hidden sm:flex items-center gap-1 font-mono text-[11px] text-muted-foreground">
            <kbd className="px-1.5 py-0.5 rounded border bg-foreground/[0.03]" style={{ borderColor: 'var(--hairline)' }}>⌘</kbd>
            <kbd className="px-1.5 py-0.5 rounded border bg-foreground/[0.03]" style={{ borderColor: 'var(--hairline)' }}>K</kbd>
          </span>
        </button>

        <div className="ml-auto flex items-center gap-2">
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={toggleAIPanel}
              data-testid={APP_SHELL.aiPanelToggle}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-primary/30 bg-primary/10 hover:bg-primary/15 text-sm font-medium transition-colors"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span>AI Mentor</span>
            </button>
            {streak != null && (
              <div className="inline-flex items-center gap-1 px-2 py-1 rounded text-sm font-medium text-muted-foreground">
                <Flame className="h-4 w-4 text-amber-400" />
                <span className="font-display text-sm">{streak}</span>
              </div>
            )}
          </div>

          {/* Theme selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                aria-label="Change theme"
                data-testid={APP_SHELL.themeToggle}
                className="h-9 w-9 flex items-center justify-center rounded-lg border hover:bg-foreground/[0.04] transition-colors"
                style={{ borderColor: 'var(--hairline)' }}
              >
                <ThemeIcon className="h-4 w-4 text-muted-foreground" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuLabel className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Theme</DropdownMenuLabel>
              <DropdownMenuItem onSelect={() => setTheme('light')} className={cn('cursor-pointer', theme === 'light' && 'text-primary')} data-testid={`${APP_SHELL.themeToggle}-light`}>
                <Sun className="h-4 w-4 mr-2" /> Light
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => setTheme('dark')} className={cn('cursor-pointer', theme === 'dark' && 'text-primary')} data-testid={`${APP_SHELL.themeToggle}-dark`}>
                <Moon className="h-4 w-4 mr-2" /> Dark
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => setTheme('system')} className={cn('cursor-pointer', theme === 'system' && 'text-primary')} data-testid={`${APP_SHELL.themeToggle}-system`}>
                <Monitor className="h-4 w-4 mr-2" /> System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <button
            onClick={() => navigate('/app/notifications')}
            data-testid={APP_SHELL.notificationsButton}
            className="relative h-9 w-9 flex items-center justify-center rounded-lg border hover:bg-foreground/[0.04] transition-colors"
            style={{ borderColor: 'var(--hairline)' }}
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4 text-muted-foreground" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-background" />
          </button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                data-testid={APP_SHELL.userMenuButton}
                className="h-9 pl-1 pr-2.5 flex items-center gap-2 rounded-lg border hover:bg-foreground/[0.04] transition-colors"
                style={{ borderColor: 'var(--hairline)' }}
              >
                <UserAvatar user={user} size="sm" data-testid={APP_SHELL.headerAvatar} />
                <span className="hidden sm:inline text-xs text-muted-foreground max-w-[110px] truncate">
                  {user?.email}
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-56 bg-[hsl(var(--surface))]/95 backdrop-blur-xl"
            >
              <DropdownMenuLabel className="text-xs text-muted-foreground font-mono uppercase tracking-wider">
                Signed in
              </DropdownMenuLabel>
              <div className="px-2 pb-2 flex items-center gap-2.5">
                <UserAvatar user={user} size="md" />
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{user?.name}</p>
                  <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={() => navigate('/app/profile')} className="cursor-pointer">
                <UserIcon className="h-4 w-4 mr-2" /> Profile
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => navigate('/app/settings')} className="cursor-pointer">
                <Settings className="h-4 w-4 mr-2" /> Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onSelect={async () => { await logout(); navigate('/login'); }}
                data-testid={LOGOUT.button}
                className="text-destructive focus:text-destructive cursor-pointer"
              >
                <LogOut className="h-4 w-4 mr-2" /> Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
