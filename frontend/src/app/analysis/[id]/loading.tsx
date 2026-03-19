import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Skeleton className="mb-4 h-8 w-72" />
      <div className="grid gap-4 lg:grid-cols-5">
        <Skeleton className="h-[70vh] lg:col-span-2" />
        <Skeleton className="h-[70vh] lg:col-span-3" />
      </div>
    </main>
  );
}
