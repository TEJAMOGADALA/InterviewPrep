import { cn } from '@/lib/utils';

function initials(name = '') {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join('') || 'P';
}

const SIZES = {
  xs: 'h-6 w-6 text-[10px]',
  sm: 'h-7 w-7 text-xs',
  md: 'h-9 w-9 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-20 w-20 text-3xl',
};

/**
 * UserAvatar (RC1.3)
 *
 * Single source of truth for rendering a user's avatar across the app.
 * Uses `user.avatar_url` when present, falls back to initials on a
 * gradient. Any component that displays a user avatar should use this
 * so a profile picture change reflects everywhere immediately.
 */
export function UserAvatar({ user, size = 'md', className, ...rest }) {
  const sizeClass = SIZES[size] || SIZES.md;
  const rounded = size === 'xl' ? 'rounded-2xl' : 'rounded-md';
  return (
    <span
      className={cn(
        sizeClass,
        rounded,
        'inline-flex items-center justify-center overflow-hidden font-display font-semibold text-white shrink-0 border border-foreground/10',
        !user?.avatar_url && 'bg-gradient-to-br from-primary to-secondary/70',
        className,
      )}
      {...rest}
    >
      {user?.avatar_url ? (
        <img
          src={user.avatar_url}
          alt={user?.name || 'Profile'}
          className="h-full w-full object-cover"
          draggable={false}
        />
      ) : (
        initials(user?.name)
      )}
    </span>
  );
}
