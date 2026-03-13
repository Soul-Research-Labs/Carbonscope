import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

const mockPush = vi.fn();
const mockReplace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  usePathname: () => "/dashboard",
  useSearchParams: () => new URLSearchParams(),
}));

const mockGetDashboard = vi.fn();
vi.mock("@/lib/api", () => ({
  getDashboard: () => mockGetDashboard(),
}));

vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { email: "test@example.com" },
    loading: false,
  }),
}));

vi.mock("@/components/ScopeChart", () => ({
  default: () => <div data-testid="scope-chart" />,
}));

import DashboardPage from "@/app/dashboard/page";

const MOCK_DATA = {
  company: { name: "Acme Corp", industry: "Technology" },
  latest_report: {
    total: 1234.5,
    scope1: 100,
    scope2: 200,
    scope3: 934.5,
    confidence: 0.87,
  },
  reports_count: 5,
  data_uploads_count: 12,
  year_over_year: [],
};

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    mockGetDashboard.mockReturnValue(new Promise(() => {})); // never resolves
    render(<DashboardPage />);
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0);
  });

  it("renders dashboard data", async () => {
    mockGetDashboard.mockResolvedValue(MOCK_DATA);
    render(<DashboardPage />);

    expect(await screen.findByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText(/Acme Corp/)).toBeInTheDocument();
    expect(screen.getByText(/Technology/)).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument(); // reports count
    expect(screen.getByText("12")).toBeInTheDocument(); // uploads count
    expect(screen.getByText("87%")).toBeInTheDocument(); // confidence
  });

  it("renders scope chart when report exists", async () => {
    mockGetDashboard.mockResolvedValue(MOCK_DATA);
    render(<DashboardPage />);

    expect(await screen.findByTestId("scope-chart")).toBeInTheDocument();
  });

  it("renders error state", async () => {
    mockGetDashboard.mockRejectedValue(new Error("Network failed"));
    render(<DashboardPage />);

    expect(await screen.findByText(/Network failed/)).toBeInTheDocument();
  });
});
