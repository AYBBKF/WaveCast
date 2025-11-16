import { Flame } from 'lucide-react';
import { motion } from 'framer-motion';

export function SplashScreen() {
  return (
    <div className="w-screen h-screen flex items-center justify-center bg-black">
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <Flame className="text-red-600" size={128} />
      </motion.div>
    </div>
  );
}
