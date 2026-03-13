"use client";

import { useEffect } from "react";

export default function SellerDashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Seller dashboard error:", error);
  }, [error]);

  return (
    <div className="p-8">
      <div className="card max-w-lg mx-auto text-center p-8">
        <div className="text-4xl mb-4">🏪</div>
        <h2 className="text-xl font-bold mb-2 text-[var(--foreground)]">
          Seller dashboard failed to load
        </h2>
        <p className="text-[var(--muted)] mb-6 text-sm">
          {error.message || "Could not load seller dashboard."}
        </p>
        <button onClick={reset} className="btn-primary">
          Retry
        </button>
      </div>
    </div>
  );
}
