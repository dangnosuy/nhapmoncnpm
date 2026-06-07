# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Smart Savings** — A savings management system (Nhập môn CNPM — Nhóm 13) with three user roles:

- **CUSTOMER** — Opens savings accounts, deposits/withdraws, views reports (client app)
- **STAFF** — Approves/rejects transactions, manages operations (staff app)
- **ADMIN** — Manages users, savings products, system configs, reports (admin app)

## Architecture

```
├── backend/                    # Flask API server
│   ├── app.py                  # App factory, blueprint registration, schema migrations
│   ├── common/                 # Shared modules
│   │   ├── db.py               # MySQL connection (mysql-connector-python)
│   │   ├── auth.py             # JWT auth, login, registration
│   │   ├── events.py           # Event system
│   │   ├── requireRole.py      # Role-check decorator
│   │   └── savings_rules.py    # Business rules (min amounts, terms)
│   ├── admin/admin.py          # Admin endpoints (users, products, configs, reports)
│   ├── staff/staff.py          # Staff endpoints (transaction approval)
│   └── client/client.py        # Customer endpoints (savings, wallet, transactions)
├── frontend/                   # React + Vite (multi-entry)
│   ├── index.html              # Admin SPA entry
│   ├── client/index.html       # Customer SPA entry (separate app)
│   ├── staff/index.html        # Staff SPA entry (separate app)
│   ├── src/                    # Admin SPA source
│   │   ├── App.jsx             # Router, role-based redirects, ProtectedRoute
│   │   ├── layouts/AdminLayout.jsx
│   │   └── pages/admin/        # Dashboard, Users, SavingsProducts, Configs, Reports
│   └── tests/                  # Playwright E2E tests (role-flow.spec.js)
├── smart_savings.sql           # DB schema + seed data (DROP/CREATE modern_savings_db)
├── requirements.txt            # Python deps
└── test_flow.py                # Python integration test script
```

### Key Design Decisions

- **Multi-entry Vite build**: Three separate HTML entry points (`index.html`, `client/index.html`, `staff/index.html`). The Vite dev server proxies `/api` to `http://localhost:5000` and redirects `/client` → `/client/`, `/staff` → `/staff/`.
- **Client/staff SPAs are standalone single-file apps**: `frontend/client/index.html` and `frontend/staff/index.html` contain all their JavaScript inline (not Vite-managed React modules). Do not edit them expecting Vite to rebuild them — they are self-contained. The admin SPA under `frontend/src/` is the only React/Vite-managed app.
- **Role-based routing**: `App.jsx` uses `ProtectedRoute` (admin SPA) and `ExternalRoleRoute` (redirects to client/staff SPAs via `window.location.replace`).
- **Schema auto-migration**: `app.py` runs `ensure_*_schema()` functions at startup to add missing columns (`account_number`, `address`, `transaction_type`, `interest_amount`).
- **Default accounts**: Admin (`admin@gmail.com` / `admin123`) and Staff (`staff@gmail.com` / `staff123`) are auto-created. Overridable via env vars.
- **Maker/Checker pattern**: Transactions go through `PENDING → APPROVED/REJECTED` workflow. Staff processes, customers initiate.
- **SSE real-time events**: `backend/common/events.py` exposes `/api/events` as a Server-Sent Events stream. Call `publish_event(type, message, roles, user_ids)` from any route handler to push live notifications to connected clients.
- **Thread-local DB proxies**: `db_conn` and `db_cursor` in `common/db.py` are thread-local proxies — import them directly at the top of each module that needs them. Never pass them as function arguments between modules or store them outside `common/`.
- **New customer welcome bonus**: Registration auto-credits 10,000,000 VND to the new `CUSTOMER`'s `wallet_balance`.

## Commands

### Backend

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database (creates modern_savings_db with user smart_savings)
mysql -u root -p < smart_savings.sql
# Default DB credentials: user=smart_savings, password=SmartSavings@2026!, db=modern_savings_db
# Override via env vars: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Run server (from repo root)
cd backend && python app.py
# → http://localhost:5000
# Smoke test: GET /api/ping

# Seed analytics mock data (Jan 2025–May 2026) — optional, for analytics charts
python seed_mock_data.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # → http://localhost:5173 (admin), /client/ (customer), /staff/ (staff)
npm run build      # Multi-entry build (main, client, staff)
npm run lint       # ESLint
```

### Testing

```bash
# E2E (Playwright) — requires BOTH backend (port 5000) and frontend dev server (port 5173) running
cd frontend && npx playwright test
npx playwright test tests/role-flow.spec.js          # run one file
npx playwright test --grep "customer"                # run matching tests

# Python integration test
python test_flow.py
```

## Database Schema (Key Tables)

| Table | Purpose |
|-------|---------|
| `users` | All roles. Fields: email, password_hash, role, wallet_balance, account_number, address |
| `savings_products` | Savings packages (term_months, interest_rate, min_days_hold) |
| `savings_accounts` | Electronic savings books (user_id, product_id, principal_balance, status) |
| `transactions` | Ledger with maker/checker (type, status PENDING/APPROVED/REJECTED, processed_by) |
| `system_configs` | Dynamic config (MIN_OPEN_AMOUNT, MIN_SAVINGS_DEPOSIT_AMOUNT, NON_TERM_MIN_DAYS) |

## API Conventions

- All routes prefixed with `/api/`
- JWT token in `Authorization: Bearer <token>` header
- Roles: `'ADMIN'`, `'STAFF'`, `'CUSTOMER'` (uppercase strings)
- JSON keys: `snake_case`
- SQL: Always parameterized with `%s` — never string interpolation
- Response messages: Vietnamese for user-facing text

## Coding Style

- **Backend**: Python 3, 4-space indent, Flask blueprints, small route handlers
- **Frontend**: React functional components, JSX, React Router v7, axios for HTTP
- Move shared logic to `backend/common/`
- Keep Vietnamese response messages consistent

## Existing Guidelines

See `docs/AGENTS.md` for additional repository guidelines (commit style, PR guidelines, security tips). The docs/AGENTS.md also documents the `rtk` CLI proxy policy for token-optimized command execution.

## Project Documents

- `docs/Project_Specification_Savings_System.md` — Full project spec (15.7K)
- `docs/detai.md` — Topic description
- `docs/LAB_COMPLETION_GUIDE.md` — Lab completion guide
- `docs/BaoCaoCNPM.docs.pdf` / `docs/BaoCaoGiuaKy_*.docx` — Course deliverables
- `docs/SKILL.md` — Skill documentation

## Notes

- No `.cursorrules`, `.cursor/`, or `.github/copilot-instructions.md` files exist
- `backend_output.log` contains server output from a previous run
- Git remote: `https://github.com/dangnosuy/nhapmoncnpm.git` (origin/main)
