import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold", {
  variants: {
    variant: {
      default: "bg-zinc-800 text-zinc-200",
      success: "bg-emerald-500/20 text-emerald-300",
      error: "bg-red-500/20 text-red-300",
      warning: "bg-amber-500/20 text-amber-300",
      primary: "bg-primary/20 text-violet-300",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
