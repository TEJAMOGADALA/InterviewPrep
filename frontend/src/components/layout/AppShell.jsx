import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { AIAssistantPanel } from './AIAssistantPanel';
import { CommandPalette } from './CommandPalette';
import { AIPanelProvider, useAIPanel } from '@/contexts/AIPanelContext';
import { CommandPaletteProvider } from '@/contexts/CommandPaletteContext';
import { MobileNav } from './MobileNav';

function ShellInner() {
  const { open: aiOpen } = useAIPanel();
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar />
      <MobileNav />
      <div className="lg:pl-[260px]">
        <Topbar />
        <main
          className={
            'transition-[padding] duration-300 ' +
            (aiOpen ? 'lg:pr-[420px]' : 'pr-0')
          }
        >
          <div className="mx-auto max-w-7xl px-5 sm:px-8 py-8">
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
    <AIPanelProvider>
      <CommandPaletteProvider>
        <ShellInner />
      </CommandPaletteProvider>
    </AIPanelProvider>
  );
}
