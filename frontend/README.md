# CarbonScope Frontend

> Next.js 15 dashboard for the CarbonScope carbon management platform.

---

## Tech Stack

| Technology                                     | Version | Purpose                                         |
| :--------------------------------------------- | :------ | :---------------------------------------------- |
| [Next.js](https://nextjs.org)                  | 15.5    | React framework (App Router, standalone output) |
| [React](https://react.dev)                     | 19.2    | UI library                                      |
| [TypeScript](https://www.typescriptlang.org)   | 5.9     | Type safety                                     |
| [Tailwind CSS](https://tailwindcss.com)        | 4.2     | Utility-first styling                           |
| [Recharts](https://recharts.org)               | 2.15    | Chart visualization                             |
| [Vitest](https://vitest.dev)                   | 4.0     | Unit testing framework                          |
| [Testing Library](https://testing-library.com) | 16.3    | Component testing utilities                     |

---

## Getting Started

### Prerequisites

- Node.js 18+ (20+ recommended)
- Backend running at `http://localhost:8000` (or set `BACKEND_URL`)

### Install & Run

```bash
npm install
npm run dev         # → http://localhost:3000
```

### Available Scripts

| Script               | Description                              |
| :------------------- | :--------------------------------------- |
| `npm run dev`        | Start development server with HMR        |
| `npm run build`      | Build for production (standalone output) |
| `npm start`          | Start production server                  |
| `npm run lint`       | Run ESLint                               |
| `npm test`           | Run Vitest test suite                    |
| `npm run test:watch` | Run Vitest in watch mode                 |

### Environment Variables

| Variable              | Default                 | Description                             |
| :-------------------- | :---------------------- | :-------------------------------------- |
| `BACKEND_URL`         | `http://localhost:8000` | Backend API URL (server-side)           |
| `NEXT_PUBLIC_API_URL` | —                       | Backend API URL (client-side, optional) |

The Next.js config rewrites `/api/*` requests to the backend, so the frontend and backend can share the same domain in production.

---

## Project Structure

```
frontend/
├── public/                          # Static assets
├── src/
│   ├── app/                         # Next.js App Router pages
│   │   ├── layout.tsx               # Root layout (auth context, fonts)
│   │   ├── page.tsx                 # Home redirect → /dashboard
│   │   ├── loading.tsx              # Global loading skeleton
│   │   ├── error.tsx                # Global error boundary
│   │   ├── not-found.tsx            # 404 page
│   │   ├── globals.css              # Tailwind imports + global styles
│   │   ├── login/                   # Login page
│   │   ├── register/                # Registration page
│   │   ├── forgot-password/         # Password reset request
│   │   ├── reset-password/          # Password reset with token
│   │   ├── dashboard/               # KPI cards, scope charts, trends
│   │   ├── upload/                  # Data upload form
│   │   ├── reports/                 # Report listing + detail
│   │   ├── recommendations/         # AI reduction strategies (per report)
│   │   │   └── [reportId]/          #   Strategy detail for specific report
│   │   ├── questionnaires/          # Questionnaire management + detail
│   │   ├── scenarios/               # Scenario listing, creation, compute
│   │   ├── supply-chain/            # Supplier network management
│   │   ├── compliance/              # Compliance report generation
│   │   ├── marketplace/             # Data marketplace
│   │   ├── alerts/                  # Alert dashboard
│   │   ├── billing/                 # Subscription & credit management
│   │   ├── audit-logs/              # Activity trail viewer
│   │   └── settings/                # User profile & company settings
│   ├── components/                  # Reusable UI components
│   │   ├── Breadcrumbs.tsx          # Navigation breadcrumb trail
│   │   ├── ConfirmDialog.tsx        # Confirmation modal for destructive actions
│   │   ├── DataTable.tsx            # Sortable, paginated data table
│   │   ├── FormField.tsx            # Form input with label, error, and hint
│   │   ├── Navbar.tsx               # Top navigation bar
│   │   ├── ScopeChart.tsx           # Scope 1/2/3 breakdown chart (Recharts)
│   │   ├── Skeleton.tsx             # Loading placeholder animation
│   │   └── Toast.tsx                # Toast notification system
│   ├── lib/                         # Utilities & services
│   │   ├── api.ts                   # Typed API client (55+ functions)
│   │   └── auth-context.tsx         # React context for JWT auth state
│   └── __tests__/                   # Test files
│       └── setup.ts                 # Vitest + Testing Library setup
├── next.config.js                   # API proxy rewrites, standalone output
├── tsconfig.json                    # TypeScript strict mode config
├── vitest.config.ts                 # Vitest with jsdom environment
├── postcss.config.mjs               # PostCSS + Tailwind CSS
├── tailwind.config.ts               # Tailwind CSS configuration
└── package.json                     # Dependencies & scripts
```

---

## Pages

| Route                         | Page                 | Description                                              |
| :---------------------------- | :------------------- | :------------------------------------------------------- |
| `/`                           | Home                 | Redirects to `/dashboard`                                |
| `/login`                      | Login                | Email/password authentication                            |
| `/register`                   | Register             | Create account + company                                 |
| `/forgot-password`            | Forgot Password      | Request password reset email                             |
| `/reset-password`             | Reset Password       | Set new password with reset token                        |
| `/dashboard`                  | Dashboard            | KPI cards, scope breakdown chart, year-over-year trends  |
| `/upload`                     | Data Upload          | Structured entry form for Scope 1/2/3 activity data      |
| `/reports`                    | Reports              | Paginated list with sorting, filtering, CSV/JSON export  |
| `/reports/[id]`               | Report Detail        | Full report with breakdown, sources, PDF export          |
| `/recommendations`            | Recommendations      | Report index for AI reduction strategies                 |
| `/recommendations/[reportId]` | Recommendations      | AI-generated reduction strategies for a specific report  |
| `/questionnaires`             | Questionnaires       | Document upload, template selection, extraction status   |
| `/questionnaires/[id]`        | Questionnaire Detail | Review AI-extracted questions, edit answers, PDF export  |
| `/scenarios`                  | Scenarios            | Scenario listing, creation, and compute                  |
| `/supply-chain`               | Supply Chain         | Supplier/buyer network, Scope 3 aggregation              |
| `/compliance`                 | Compliance           | Generate GHG Protocol / CDP / TCFD / SBTi reports        |
| `/marketplace`                | Marketplace          | Browse, purchase, list, and withdraw data listings       |
| `/marketplace/seller`         | Seller Dashboard     | Revenue summary, sales table, active listings            |
| `/alerts`                     | Alerts               | Emission threshold alerts with acknowledgement           |
| `/billing`                    | Billing              | Subscription plans, credit balance, plan management      |
| `/audit-logs`                 | Audit Logs           | Activity trail with pagination and action filters        |
| `/settings`                   | Settings             | User profile, password change, company profile, webhooks |

---

## Components

### Navbar

Top navigation bar with links to all major pages. Highlights the active route. Includes mobile-responsive hamburger menu and user dropdown.

### ScopeChart

Recharts-based pie/bar chart for Scope 1/2/3 emission breakdown visualization. Used on the dashboard and report detail pages.

### DataTable

Generic sortable, paginated table component. Supports column sorting (asc/desc), pagination controls, and empty state display.

### FormField

Wrapper for form inputs that provides consistent label, error message, and hint text rendering. Used across all auth and data entry forms.

### ConfirmDialog

Modal dialog for confirming destructive actions (delete report, remove supplier, etc.). Supports customizable title, message, and button labels with danger/warning variants.

### Breadcrumbs

Navigation trail component for nested pages (e.g., Reports → Report #5). Supports custom labels and links.

### Skeleton

Animated loading placeholder. Available in multiple sizes and shapes for cards, text, and tables.

### Toast

Notification system with success, error, warning, and info variants. Auto-dismisses after a configurable timeout. Supports manual close.

---

## API Client

The typed API client at `src/lib/api.ts` provides 55+ functions covering all backend endpoints:

- **Auto-auth:** Attaches JWT Bearer token from `localStorage`
- **Token refresh:** Automatically refreshes expired tokens on 401 response and retries
- **Type safety:** All request/response bodies are typed
- **Error handling:** Throws `ApiError` with status code and message

```typescript
import { getReports, createEstimate } from "@/lib/api";

// Fetch reports with pagination
const { items, total } = await getReports({ limit: 20, offset: 0 });

// Run emission estimation
const report = await createEstimate({ upload_id: 1 });
```

---

## Auth Context

The `AuthProvider` at `src/lib/auth-context.tsx` manages authentication state:

- Stores JWT token and user info in React context
- Provides `login()`, `logout()`, `register()` functions
- Auto-refreshes tokens before expiry
- Redirects unauthenticated users to `/login`

```tsx
import { useAuth } from "@/lib/auth-context";

function MyComponent() {
  const { user, logout } = useAuth();
  return <button onClick={logout}>Sign out, {user?.name}</button>;
}
```

---

## Testing

### Run Tests

```bash
npm test              # Run full suite (83 tests)
npm run test:watch    # Watch mode for development
```

### Test Configuration

- **Framework:** Vitest 4.0
- **Environment:** jsdom
- **Setup:** `src/__tests__/setup.ts` (Testing Library matchers)
- **Pattern:** `src/**/*.test.{ts,tsx}`

### Test Coverage

| Test File                 | Coverage                                              |
| :------------------------ | :---------------------------------------------------- |
| `Breadcrumbs.test.tsx`    | Rendering, links, accessibility, separators           |
| `ConfirmDialog.test.tsx`  | Open/close, confirm/cancel, variants, custom labels   |
| `DataTable.test.tsx`      | Sorting, pagination, empty states, rendering          |
| `FormField.test.tsx`      | Labels, errors, hints, children, accessibility        |
| `Navbar.test.tsx`         | Navigation links, active states, mobile menu          |
| `Skeleton.test.tsx`       | Skeleton variants, animation, sizing                  |
| `Toast.test.tsx`          | Toast types, auto-dismiss, manual close               |
| `api.test.ts`             | ApiError, auth headers, error handling                |
| `api-new-methods.test.ts` | Credit ledger, delete account, supply chain, webhooks |
| `LoginPage.test.tsx`             | Form submission, validation, error handling            |
| `DashboardPage.test.tsx`         | KPI cards, API data rendering, empty states           |
| `RecommendationsPage.test.tsx`   | Strategy listing, navigation, data display            |
| `SellerDashboardPage.test.tsx`   | Revenue summary, sales table, pagination              |

### Writing Tests

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConfirmDialog } from "@/components/ConfirmDialog";

test("calls onConfirm when confirmed", async () => {
  const onConfirm = vi.fn();
  render(
    <ConfirmDialog
      isOpen={true}
      title="Delete?"
      message="This cannot be undone."
      onConfirm={onConfirm}
      onCancel={() => {}}
    />,
  );
  await userEvent.click(screen.getByRole("button", { name: /confirm/i }));
  expect(onConfirm).toHaveBeenCalledOnce();
});
```

---

## UI Features

- **Responsive layout** — Mobile-friendly with adaptive navigation and card-based data tables
- **Toast notifications** — Success, error, warning, info toasts with auto-dismiss
- **Confirmation dialogs** — All destructive actions require confirmation
- **Loading skeletons** — Animated placeholders during data fetching on all pages
- **Breadcrumb navigation** — Trail on all detail/nested pages
- **Copy-to-clipboard** — One-click copy with "Copied!" feedback on webhook URLs
- **URL query state sync** — Filter state persisted in URL params (marketplace, scenarios)
- **Dark/light mode** — Persistent theme toggle with system preference detection
- **Accessibility** — Skip-to-content link, focus indicators, `prefers-reduced-motion` support, `htmlFor`/`id` labels, ARIA attributes
- **Error boundaries** — Graceful error handling on key routes

---

## Build & Deploy

### Production Build

```bash
npm run build
```

Produces a standalone server at `.next/standalone/` (configured via `output: "standalone"` in `next.config.js`).

### Run Production Server

```bash
node .next/standalone/server.js
```

Or via npm:

```bash
npm start -- -p 3000
```

### Docker

The Dockerfile includes a multi-stage build for the frontend:

1. **frontend-deps** — Install npm packages
2. **frontend-build** — Build Next.js application
3. **frontend** — Minimal runtime with standalone output

The container runs as the non-root `node` user.

### Environment

Set `BACKEND_URL` to the backend API URL for server-side API proxy:

```bash
BACKEND_URL=http://backend:8000 node .next/standalone/server.js
```
