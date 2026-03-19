"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

const links = [
  { href: "/", label: "Overview" },
  { href: "/analyze", label: "New Analysis" },
  { href: "/history", label: "History" },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-border/80 bg-background/90 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-primary pulse-dot" />
          <span className="text-lg font-bold tracking-tight">Proctor</span>
        </Link>
        <div className="flex items-center gap-4">
          <nav className="flex items-center gap-1">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link key={link.href} href={link.href}>
                  <Button variant={active ? "default" : "ghost"} size="sm" className="text-xs sm:text-sm">
                    {link.label}
                  </Button>
                </Link>
              );
            })}
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
