import { Bell, Command, Search, LogOut, User as UserIcon, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useCommandPalette } from '@/contexts/CommandPaletteContext';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { APP_SHELL, LOGOUT } from '@/constants/testIds';
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuSeparator, DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { Sparkles } from 'lucide-react';

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((s) => s[0]?.toUpperCase()).join('') || 'P';
}

export function Topbar() {
  const { user, logout } = useAuth();
  const { setOpen: setCmdOpen } = useCommandPalette();
  const { toggle: toggleAIPanel } = useAIPanel();
  const navigate = useNavigate();

  return (
    <header
      data-testid={APP_SHELL.topbar}
      className="sticky top-0 z-20 h-16 border-b border-white/[0.06] bg-background/70 backdrop-blur-xl"
    >
      <div className="h-full flex items-center gap-4 px-6">
        <button
          type="button"
          onClick={() => setCmdOpen(true)}
          data-testid={APP_SHELL.globalSearch}
          className="group flex-1 max-w-xl flex items-center gap-3 px-3.5 py-2 rounded-lg border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04] transition-colors"
        >
          <Search className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Search commands, missions, topics…</span>
          <span className="ml-auto flex items-center gap-1 font-mono text-[11px] text-muted-foreground">
            <kbd className="px-1.5 py-0.5 rounded border border-white/10 bg-white/[0.03]">⌘</kbd>
            <kbd className="px-1.5 py-0.5 rounded border border-white/10 bg-white/[0.03]">K</kbd>
          </span>
        </button>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={toggleAIPanel}
            data-testid={APP_SHELL.aiPanelToggle}
            className="hidden md:inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-primary/30 bg-primary/10 hover:bg-primary/15 text-sm font-medium transition-colors"
          >
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            <span>AI Mentor</span>
          </button>

          <button
            onClick={() => navigate('/app/notifications')}
            data-testid={APP_SHELL.notificationsButton}
            className="relative h-9 w-9 flex items-center justify-center rounded-lg border border-white/[0.08] hover:bg-white/[0.04] transition-colors"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4 text-muted-foreground" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-background" />
          </button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                data-testid={APP_SHELL.userMenuButton}
                className="h-9 pl-1 pr-2.5 flex items-center gap-2 rounded-lg border border-white/[0.08] hover:bg-white/[0.04] transition-colors"
              >
                <span className="h-7 w-7 rounded-md bg-gradient-to-br from-primary to-secondary/70 flex items-center justify-center font-display text-xs font-semibold text-white">
                  {initials(user?.name)}
                </span>
                <span className="hidden sm:inline text-xs text-muted-foreground max-w-[110px] truncate">
                  {user?.email}
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-56 bg-[hsl(var(--surface))]/95 border-white/10 backdrop-blur-xl"
            >
              <DropdownMenuLabel className="text-xs text-muted-foreground font-mono uppercase tracking-wider">
                Signed in
              </DropdownMenuLabel>
              <div className="px-2 pb-2">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem onSelect={() => navigate('/app/profile')} className="cursor-pointer">
                <UserIcon className="h-4 w-4 mr-2" /> Profile
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => navigate('/app/settings')} className="cursor-pointer">
                <Settings className="h-4 w-4 mr-2" /> Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-white/10" />
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
