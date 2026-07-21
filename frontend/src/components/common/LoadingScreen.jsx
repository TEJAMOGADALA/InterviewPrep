import { motion } from 'framer-motion';

export function LoadingScreen({ label = 'Loading' }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center gap-4"
      >
        <div className="relative h-12 w-12">
          <span className="absolute inset-0 rounded-full border border-white/10" />
          <span className="absolute inset-0 rounded-full border-t-2 border-primary animate-spin" />
        </div>
        <span className="overline">{label}</span>
      </motion.div>
    </div>
  );
}
