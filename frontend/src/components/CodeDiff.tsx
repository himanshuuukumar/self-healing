"use client";

import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CodeDiffProps {
  before: string;
  after: string;
}

export function CodeDiff({ before, after }: CodeDiffProps) {
  const [copied, setCopied] = useState(false);

  const diffText = `${before
    .split("\n")
    .map((line) => `- ${line}`)
    .join("\n")}\n${after
    .split("\n")
    .map((line) => `+ ${line}`)
    .join("\n")}`;

  const copyFix = async () => {
    await navigator.clipboard.writeText(after);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  };

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-zinc-950">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <p className="text-xs uppercase tracking-wide text-muted">Suggested Diff</p>
        <Button variant="outline" size="sm" onClick={copyFix} className="h-8">
          {copied ? <Check className="mr-1 h-4 w-4" /> : <Copy className="mr-1 h-4 w-4" />} Copy Fix
        </Button>
      </div>
      <SyntaxHighlighter language="python" style={oneDark} customStyle={{ margin: 0, fontSize: "0.8rem" }}>
        {diffText}
      </SyntaxHighlighter>
    </div>
  );
}
