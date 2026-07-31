import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { AIAssistantPanel } from './AIAssistantPanel';
import { CommandPalette } from './CommandPalette';
import { MobileNav } from './MobileNav';
import { CommandPaletteProvider } from '@/contexts/CommandPaletteContext';
import { useAIPanel } from '@/contexts/AIPanelContext';
import { useUILayout } from '@/contexts/UILayoutContext';
import { cn } from '@/lib/utils';

function ShellInner() {
  const { open: aiOpen } = useAIPanel();
  const { sidebarCollapsed } = useUILayout();

  const sidebarWidth = sidebarCollapsed ? 72 : 260;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar />
      <MobileNav />
      <div
        style={{ paddingLeft: undefined }}
        className={cn(
          'transition-[padding] duration-300 ease-out',
          sidebarCollapsed ? 'lg:pl-[72px]' : 'lg:pl-[260px]',
        )}
      >
        <Topbar />
        <main
          className={cn(
            'transition-[padding] duration-300',
            aiOpen ? 'lg:pr-[420px]' : 'pr-0',
          )}
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            <Outlet />
          </div>
        </main>
      </div>
      <AIAssistantPanel />
      <CommandPalette />
    </div>
  );
}

export function AppShell() {
  return (
    <CommandPaletteProvider>
      <ShellInner />
    </CommandPaletteProvider>
  );
}
