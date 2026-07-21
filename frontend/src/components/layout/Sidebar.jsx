import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { NAV_ITEMS } from '@/config/navigation';
import { Logo } from '@/components/common/Logo';
import { APP_SHELL } from '@/constants/testIds';
import { cn } from '@/lib/utils';

export function Sidebar() {
  return (
    <aside
      data-testid={APP_SHELL.sidebar}
      className="hidden lg:flex flex-col fixed inset-y-0 left-0 z-30 w-[260px] border-r border-white/[0.06] bg-[hsl(var(--surface))]/60 backdrop-blur-xl"
    >
      <div className="px-6 pt-6 pb-8">
        <Logo />
      </div>

      <div className="px-4">
        <div className="overline px-2 mb-3">Workspace</div>
      </div>

      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.key}
              to={item.path}
              data-testid={`${APP_SHELL.sidebarLink}-${item.key}`}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-foreground border border-primary/30'
                    : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.03] border border-transparent',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={cn('h-4 w-4 transition-colors',
                      isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground')}
                  />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.span
                      layoutId="sidebar-indicator"
                      className="ml-auto h-1.5 w-1.5 rounded-full bg-primary"
                    />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="px-4 py-5 border-t border-white/[0.06]">
        <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
          <div className="overline mb-1">Preview build</div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            You are on <span className="text-foreground">Foundation v0.1</span>. Mission engine ships in the next drop.
          </p>
        </div>
      </div>
    </aside>
  );
}
