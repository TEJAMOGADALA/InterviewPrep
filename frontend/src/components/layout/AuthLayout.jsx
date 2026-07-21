import { motion } from 'framer-motion';
import { Logo } from '@/components/common/Logo';

export function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 py-10 overflow-hidden">
      {/* Ambient background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 grid-noise opacity-40" />
        <div className="absolute -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-[-160px] right-[-120px] h-[480px] w-[480px] rounded-full bg-secondary/10 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <div className="mb-8 flex justify-center">
          <Logo size="lg" />
        </div>

        <div className="rounded-2xl border border-white/[0.08] bg-[hsl(var(--surface))]/70 backdrop-blur-xl p-8">
          <div className="mb-6">
            <h1 className="font-display text-2xl font-semibold tracking-tight">{title}</h1>
            {subtitle && (
              <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>
          {children}
        </div>

        {footer && (
          <p className="mt-6 text-center text-sm text-muted-foreground">{footer}</p>
        )}
      </motion.div>
    </div>
  );
}
