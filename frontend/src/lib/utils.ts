import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function repoNameFromUrl(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.pathname.replace(/^\//, "");
  } catch {
    return url;
  }
}

export function githubBlobUrl(repoUrl: string, file: string, line: number): string {
  const normalizedRepo = repoUrl.replace(/\.git$/, "");
  return `${normalizedRepo}/blob/main/${file}#L${line}`;
}
