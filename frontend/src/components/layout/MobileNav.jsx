import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { NAV_ITEMS } from '@/config/navigation';
import { Logo } from '@/components/common/Logo';
import { cn } from '@/lib/utils';

export function MobileNav() {
  const [open, setOpen] = useState(false);
  return (
    <div className="lg:hidden">
      <button
        onClick={() => setOpen(true)}
        aria-label="Open navigation"
        className="fixed top-3.5 left-4 z-40 h-9 w-9 flex items-center justify-center rounded-lg border border-white/10 bg-[hsl(var(--surface))]/80 backdrop-blur-xl"
      >
        <Menu className="h-4 w-4" />
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <aside className="relative w-72 h-full bg-[hsl(var(--surface))]/95 backdrop-blur-2xl border-r border-white/10 p-5 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <Logo />
              <button
                onClick={() => setOpen(false)}
                className="h-8 w-8 flex items-center justify-center rounded-md border border-white/10"
                aria-label="Close navigation"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <nav className="space-y-1">
              {NAV_ITEMS.map((n) => {
                const Icon = n.icon;
                return (
                  <NavLink
                    key={n.key}
                    to={n.path}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                        isActive
                          ? 'bg-primary/10 text-foreground border border-primary/30'
                          : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.03]',
                      )
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {n.label}
                  </NavLink>
                );
              })}
            </nav>
          </aside>
        </div>
      )}
    </div>
  );
}
