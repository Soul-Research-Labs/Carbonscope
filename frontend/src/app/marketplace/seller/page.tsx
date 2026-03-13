"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import Breadcrumbs from "@/components/Breadcrumbs";
import { PageSkeleton } from "@/components/Skeleton";
import {
  getMyMarketplaceSales,
  getMyMarketplaceRevenue,
  type DataPurchaseOut,
  type SellerRevenue,
  type PaginatedResponse,
} from "@/lib/api";

const PAGE_SIZE = 20;

export default function SellerDashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [revenue, setRevenue] = useState<SellerRevenue | null>(null);
  const [sales, setSales] = useState<PaginatedResponse<DataPurchaseOut> | null>(
    null,
  );
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  const [fetching, setFetching] = useState(true);

  const fetchData = useCallback(async () => {
    setFetching(true);
    setError("");
    try {
      const [rev, salesRes] = await Promise.all([
        getMyMarketplaceRevenue(),
        getMyMarketplaceSales({ limit: PAGE_SIZE, offset }),
      ]);
      setRevenue(rev);
      setSales(salesRes);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load seller data");
    } finally {
      setFetching(false);
    }
  }, [offset]);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
      return;
    }
    if (user) fetchData();
  }, [user, loading, router, fetchData]);

  if (loading || (fetching && !sales)) {
    return <PageSkeleton />;
  }

  const totalPages = sales ? Math.ceil(sales.total / PAGE_SIZE) : 0;
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-8">
      <Breadcrumbs
        items={[
          { label: "Marketplace", href: "/marketplace" },
          { label: "Seller Dashboard" },
        ]}
      />

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Seller Dashboard</h1>
        <Link href="/marketplace" className="btn-secondary text-sm">
          ← Back to Marketplace
        </Link>
      </div>

      {error && <div className="text-[var(--danger)] text-sm">{error}</div>}

      {/* Revenue summary cards */}
      {revenue && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <p className="text-[var(--muted)] text-sm">Total Revenue</p>
            <p className="text-2xl font-bold text-[var(--primary)]">
              {revenue.total_revenue_credits.toLocaleString()} credits
            </p>
          </div>
          <div className="card">
            <p className="text-[var(--muted)] text-sm">Total Sales</p>
            <p className="text-2xl font-bold">{revenue.total_sales}</p>
          </div>
          <div className="card">
            <p className="text-[var(--muted)] text-sm">Active Listings</p>
            <p className="text-2xl font-bold">{revenue.active_listings}</p>
          </div>
        </div>
      )}

      {/* Sales table */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Sales</h2>
        {sales && sales.items.length === 0 ? (
          <p className="text-[var(--muted)] text-center py-8">
            No sales yet. List data on the{" "}
            <Link
              href="/marketplace"
              className="text-[var(--primary)] underline"
            >
              marketplace
            </Link>{" "}
            to get started.
          </p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--card-border)]">
                    <th className="text-left py-2 px-3 text-[var(--muted)]">
                      Listing
                    </th>
                    <th className="text-left py-2 px-3 text-[var(--muted)]">
                      Data Type
                    </th>
                    <th className="text-right py-2 px-3 text-[var(--muted)]">
                      Price
                    </th>
                    <th className="text-right py-2 px-3 text-[var(--muted)]">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sales?.items.map((sale) => (
                    <tr
                      key={sale.id}
                      className="border-b border-[var(--card-border)]/50"
                    >
                      <td className="py-2 px-3 font-medium">
                        {sale.listing?.title ?? "—"}
                      </td>
                      <td className="py-2 px-3 text-[var(--muted)]">
                        {sale.listing?.data_type?.replace(/_/g, " ") ?? "—"}
                      </td>
                      <td className="py-2 px-3 text-right font-medium">
                        {sale.price_credits.toLocaleString()} cr
                      </td>
                      <td className="py-2 px-3 text-right text-[var(--muted)]">
                        {new Date(sale.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-[var(--card-border)]">
                <button
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  disabled={offset === 0}
                  className="btn-secondary text-sm disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-sm text-[var(--muted)]">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                  disabled={currentPage >= totalPages}
                  className="btn-secondary text-sm disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
