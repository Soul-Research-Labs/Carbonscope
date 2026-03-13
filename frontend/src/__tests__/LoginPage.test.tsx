import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

const mockLogin = vi.fn();
vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({ login: mockLogin }),
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

vi.mock("@/components/FormField", () => ({
  FormField: ({
    label,
    type,
    value,
    onChange,
    ...rest
  }: {
    label: string;
    type: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  }) => (
    <label>
      {label}
      <input type={type} value={value} onChange={onChange} {...rest} />
    </label>
  ),
}));

import LoginPage from "@/app/login/page";

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders sign-in form", () => {
    render(<LoginPage />);
    expect(screen.getByText("🌿 CarbonScope")).toBeInTheDocument();
    expect(screen.getByText("Sign In")).toBeInTheDocument();
    expect(screen.getByText("Forgot password?")).toBeInTheDocument();
  });

  it("calls login on submit", async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "secret123" },
    });
    fireEvent.click(screen.getByText("Sign In"));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("user@test.com", "secret123");
    });
  });

  it("shows 401 error message", async () => {
    const err = Object.assign(new Error("Unauthorized"), { status: 401 });
    mockLogin.mockRejectedValueOnce(err);
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "bad@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByText("Sign In"));

    expect(
      await screen.findByText("Invalid email or password."),
    ).toBeInTheDocument();
  });

  it("shows rate limit error", async () => {
    const err = Object.assign(new Error("Rate limited"), { status: 429 });
    mockLogin.mockRejectedValueOnce(err);
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "pass" },
    });
    fireEvent.click(screen.getByText("Sign In"));

    expect(
      await screen.findByText("Too many requests. Please wait and try again."),
    ).toBeInTheDocument();
  });

  it("has links to register and forgot password", () => {
    render(<LoginPage />);
    const forgotLink = screen.getByText("Forgot password?");
    expect(forgotLink.closest("a")).toHaveAttribute("href", "/forgot-password");
  });
});
