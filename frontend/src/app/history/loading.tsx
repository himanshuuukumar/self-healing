import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Skeleton className="mb-3 h-10 w-64" />
      <Skeleton className="mb-6 h-11 w-72" />
      <Skeleton className="h-96 w-full" />
    </main>
  );
}
