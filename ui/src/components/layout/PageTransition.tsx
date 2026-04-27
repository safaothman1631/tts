import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useSettingsStore } from '@/stores/settings';

/** Wraps the routed page in a fade+slide transition (skipped if reduceMotion). */
export function PageTransition() {
  const location = useLocation();
  const reduce = useSettingsStore((s) => s.reduceMotion);

  if (reduce) return <Outlet />;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
        className="h-full"
      >
        <Outlet />
      </motion.div>
    </AnimatePresence>
  );
}
