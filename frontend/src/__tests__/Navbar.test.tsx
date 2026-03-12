import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

// Mock next/navigation
const mockPathname = vi.fn(() => "/reports");
vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname(),
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock auth context
vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { email: "test@example.com" },
    logout: vi.fn(),
  }),
}));

import Navbar from "@/components/Navbar";

describe("Navbar", () => {
  it("highlights exact route match", () => {
    mockPathname.mockReturnValue("/reports");
    render(<Navbar />);
    const reportLinks = screen.getAllByText(/Reports/);
    const desktopLink = reportLinks[0];
    expect(desktopLink.className).toContain("bg-[var(--primary)]");
  });

  it("highlights parent nav item on deep route", () => {
    mockPathname.mockReturnValue("/reports/abc123");
    render(<Navbar />);
    const reportLinks = screen.getAllByText(/Reports/);
    const desktopLink = reportLinks[0];
    expect(desktopLink.className).toContain("bg-[var(--primary)]");
  });

  it("does not highlight non-matching routes", () => {
    mockPathname.mockReturnValue("/reports/abc123");
    render(<Navbar />);
    const settingsLinks = screen.getAllByText(/Settings/);
    const desktopLink = settingsLinks[0];
    expect(desktopLink.className).not.toContain("bg-[var(--primary)]");
  });

  it("does not highlight dashboard for non-dashboard deep routes", () => {
    mockPathname.mockReturnValue("/reports/abc123");
    render(<Navbar />);
    const dashboardLinks = screen.getAllByText(/Dashboard/);
    const desktopLink = dashboardLinks[0];
    expect(desktopLink.className).not.toContain("bg-[var(--primary)]");
  });
});
