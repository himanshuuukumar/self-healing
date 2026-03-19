"use client";

import { motion } from "framer-motion";

export function AnimatedGrid() {
  return (
    <motion.div
      className="animated-grid pointer-events-none absolute inset-0 opacity-35"
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.35 }}
      transition={{ duration: 1.2 }}
    />
  );
}
