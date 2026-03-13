import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

const mockReplace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace, push: vi.fn() }),
  usePathname: () => "/marketplace/seller",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

const mockGetRevenue = vi.fn();
const mockGetSales = vi.fn();
vi.mock("@/lib/api", () => ({
  getMyMarketplaceRevenue: () => mockGetRevenue(),
  getMyMarketplaceSales: (...args: unknown[]) => mockGetSales(...args),
}));

vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { email: "seller@test.com" },
    loading: false,
  }),
}));

vi.mock("@/components/Breadcrumbs", () => ({
  default: () => <nav data-testid="breadcrumbs" />,
}));

import SellerDashboardPage from "@/app/marketplace/seller/page";

const MOCK_REVENUE = {
  total_revenue_credits: 5000,
  total_sales: 12,
  active_listings: 3,
};

const MOCK_SALES = {
  items: [
    {
      id: "p1",
      listing_id: "l1",
      buyer_company_id: "c1",
      price_credits: 100,
      purchased_at: "2024-01-15T10:00:00Z",
      listing: { title: "EU Carbon Data 2024", data_type: "emissions" },
    },
  ],
  total: 1,
};

describe("SellerDashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders revenue summary cards", async () => {
    mockGetRevenue.mockResolvedValue(MOCK_REVENUE);
    mockGetSales.mockResolvedValue(MOCK_SALES);
    render(<SellerDashboardPage />);

    expect(await screen.findByText(/5,000 credits/)).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("renders sales table", async () => {
    mockGetRevenue.mockResolvedValue(MOCK_REVENUE);
    mockGetSales.mockResolvedValue(MOCK_SALES);
    render(<SellerDashboardPage />);

    expect(await screen.findByText("EU Carbon Data 2024")).toBeInTheDocument();
    expect(screen.getByText("emissions")).toBeInTheDocument();
  });

  it("shows empty sales message when no sales", async () => {
    mockGetRevenue.mockResolvedValue({
      total_revenue_credits: 0,
      total_sales: 0,
      active_listings: 0,
    });
    mockGetSales.mockResolvedValue({ items: [], total: 0 });
    render(<SellerDashboardPage />);

    expect(await screen.findByText(/no sales/i)).toBeInTheDocument();
  });

  it("shows error on API failure", async () => {
    mockGetRevenue.mockRejectedValue(new Error("Forbidden"));
    mockGetSales.mockResolvedValue({ items: [], total: 0 });
    render(<SellerDashboardPage />);

    expect(await screen.findByText(/Forbidden/)).toBeInTheDocument();
  });
});
