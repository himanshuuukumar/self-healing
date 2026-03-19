import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Skeleton className="mb-3 h-10 w-64" />
      <Skeleton className="h-64 w-full" />
    </main>
  );
}
