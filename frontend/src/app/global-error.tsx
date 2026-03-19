"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body className="bg-background text-foreground">
        <main className="mx-auto max-w-3xl px-4 py-16 text-center">
          <h2 className="text-3xl font-bold tracking-tight">Unexpected application error</h2>
          <p className="mt-3 text-zinc-300">{error.message}</p>
          <Button className="mt-6" onClick={reset}>
            Recover
          </Button>
        </main>
      </body>
    </html>
  );
}
