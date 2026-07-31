import { NavLink, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { NAV_ITEMS } from '@/config/navigation';
import { Logo } from '@/components/common/Logo';
import { APP_SHELL } from '@/constants/testIds';
import { cn } from '@/lib/utils';
import { useUILayout } from '@/contexts/UILayoutContext';
import { useAuth } from '@/contexts/AuthContext';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { UserAvatar } from '@/components/common/UserAvatar';

export function Sidebar() {
  const { sidebarCollapsed } = useUILayout();
  const { user } = useAuth();

  return (
    <aside
      data-testid={APP_SHELL.sidebar}
      data-collapsed={sidebarCollapsed ? 'true' : 'false'}
      className={cn(
        'hidden lg:flex flex-col fixed inset-y-0 left-0 z-30 border-r bg-[hsl(var(--surface))]/60 backdrop-blur-xl transition-[width] duration-300 ease-out',
        sidebarCollapsed ? 'w-[72px]' : 'w-[260px]',
      )}
      style={{ borderColor: 'var(--hairline)' }}
    >
      <div className={cn('pt-6 pb-6 transition-[padding] duration-300', sidebarCollapsed ? 'px-3' : 'px-6')}>
        <Logo compact={sidebarCollapsed} />
      </div>

      {!sidebarCollapsed && (
        <div className="px-4">
          <div className="overline px-2 mb-3">Workspace</div>
        </div>
      )}

      <TooltipProvider delayDuration={100}>
        <nav className={cn('flex-1 space-y-1 overflow-y-auto overflow-x-hidden', sidebarCollapsed ? 'px-2' : 'px-3')}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const link = (
              <NavLink
                key={item.key}
                to={item.path}
                data-testid={`${APP_SHELL.sidebarLink}-${item.key}`}
                className={({ isActive }) =>
                  cn(
                    'group relative flex items-center rounded-lg text-sm font-medium transition-colors',
                    sidebarCollapsed ? 'justify-center h-10 w-10 mx-auto' : 'gap-3 px-3 py-2.5',
                    isActive
                      ? 'bg-primary/10 text-foreground border border-primary/30'
                      : 'text-muted-foreground hover:text-foreground hover:bg-foreground/[0.04] border border-transparent',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={cn('h-4 w-4 shrink-0 transition-colors',
                        isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground')}
                    />
                    {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                    {isActive && !sidebarCollapsed && (
                      <motion.span
                        layoutId="sidebar-indicator"
                        className="ml-auto h-1.5 w-1.5 rounded-full bg-primary"
                      />
                    )}
                    {isActive && sidebarCollapsed && (
                      <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-r bg-primary" />
                    )}
                  </>
                )}
              </NavLink>
            );
            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.key}>
                  <TooltipTrigger asChild>{link}</TooltipTrigger>
                  <TooltipContent side="right" className="font-medium">{item.label}</TooltipContent>
                </Tooltip>
              );
            }
            return link;
          })}
        </nav>
      </TooltipProvider>

      {/* User profile block — shows the uploaded profile picture (or initials
          fallback) so the sidebar always reflects the signed-in user. Stays in
          sync with the Topbar avatar because both consume the same
          `useAuth().user` state. */}
      <div className={cn('border-t shrink-0 transition-[padding] duration-300', sidebarCollapsed ? 'p-2' : 'p-3')} style={{ borderColor: 'var(--hairline)' }}>
        <TooltipProvider delayDuration={200}>
          {sidebarCollapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  to="/app/profile"
                  data-testid={APP_SHELL.sidebarAvatar}
                  className="flex items-center justify-center rounded-lg hover:bg-foreground/[0.04] transition-colors p-1.5"
                  aria-label="Open profile"
                >
                  <UserAvatar user={user} size="md" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right" className="font-medium">
                {user?.name || 'Profile'}
              </TooltipContent>
            </Tooltip>
          ) : (
            <Link
              to="/app/profile"
              data-testid={APP_SHELL.sidebarAvatar}
              className="flex items-center gap-3 rounded-lg border hairline bg-foreground/[0.02] hover:bg-foreground/[0.04] transition-colors px-3 py-2.5 group"
            >
              <UserAvatar user={user} size="md" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate group-hover:text-foreground">
                  {user?.name || 'Profile'}
                </div>
                <div className="text-[11px] text-muted-foreground truncate">
                  {user?.email || 'Update your profile'}
                </div>
              </div>
            </Link>
          )}
        </TooltipProvider>
      </div>
    </aside>
  );
}
