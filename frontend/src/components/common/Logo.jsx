import { motion } from 'framer-motion';

export function Logo({ size = 'md', withText = true }) {
  const box = size === 'lg' ? 'h-10 w-10' : size === 'sm' ? 'h-7 w-7' : 'h-9 w-9';
  const text = size === 'lg' ? 'text-2xl' : size === 'sm' ? 'text-base' : 'text-lg';
  return (
    <div className="flex items-center gap-2.5">
      <motion.div
        initial={{ rotate: -20, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        className={`${box} relative rounded-xl bg-gradient-to-br from-primary to-secondary/70 border border-white/10 flex items-center justify-center overflow-hidden`}
      >
        <div className="absolute inset-0 opacity-20 grid-noise" />
        <span className="font-display text-white font-bold text-sm relative">P</span>
        <span className="absolute -bottom-1 -right-1 h-2.5 w-2.5 rounded-full bg-white/90 border-2 border-background" />
      </motion.div>
      {withText && (
        <div className="leading-none">
          <span className={`font-display font-semibold tracking-tight ${text} text-foreground`}>
            PrepOS
          </span>
          <span className="block mt-1 overline text-[10px]">Interview OS</span>
        </div>
      )}
    </div>
  );
}
