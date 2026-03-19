"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bug, Cpu, WandSparkles } from "lucide-react";
import { AnimatedGrid } from "@/components/AnimatedGrid";
import { Button } from "@/components/ui/button";

const steps = [
  {
    icon: Bug,
    title: "Submit Repo",
    text: "Connect GitHub and logs in one secure intake.",
  },
  {
    icon: Cpu,
    title: "AI Analyzes",
    text: "Proctor clones, indexes, correlates errors, and finds root causes.",
  },
  {
    icon: WandSparkles,
    title: "Get Fix",
    text: "See file-level diagnosis and a patch proposal streamed live.",
  },
];

export default function Home() {
  return (
    <main className="relative overflow-hidden">
      <AnimatedGrid />
      <section className="relative mx-auto flex min-h-[70vh] max-w-7xl flex-col justify-center px-4 py-24 sm:px-6 lg:px-8">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="mb-5 font-mono text-xs uppercase tracking-[0.22em] text-violet-300"
        >
          Autonomous Debugging Platform
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.55 }}
          className="max-w-4xl text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl"
        >
          Proctor turns production chaos into precise code fixes.
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.55 }}
          className="mt-5 max-w-2xl text-base text-zinc-300 sm:text-lg"
        >
          Stream root-cause analysis from logs, pinpoint exact lines, and ship confident fixes in minutes.
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mt-8">
          <Link href="/analyze">
            <Button size="lg" className="group">
              Start Debugging
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </Link>
        </motion.div>
      </section>

      <section className="relative mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
        <h2 className="mb-6 text-2xl font-bold tracking-tight">How it works</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * index }}
                className="glass rounded-xl p-5"
              >
                <Icon className="mb-3 h-7 w-7 text-violet-300" />
                <h3 className="text-lg font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm text-zinc-300">{step.text}</p>
              </motion.div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
