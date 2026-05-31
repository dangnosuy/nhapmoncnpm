# Repository Guidelines

## Project Structure & Module Organization

- `backend/app.py` creates the Flask app, enables CORS, and registers API blueprints.
- `backend/common/` contains shared database, authentication, and role-check helpers.
- `backend/staff/` contains staff-facing transaction and account endpoints plus endpoint notes.
- `smart_savings.sql` defines and seeds the MySQL database schema.
- `requirements.txt` lists Python runtime dependencies.
- Report documents (`*.docx`, `*.pdf`) are project deliverables, not application source.

Do not commit generated caches such as `__pycache__/` or `*.pyc`.

## Build, Test, and Development Commands

Create and activate a virtual environment before installing dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Initialize the database locally:

```bash
mysql -u root -p < smart_savings.sql
```

Run the backend from the repository root:

```bash
cd backend
python app.py
```

The API runs on `http://localhost:5000`; use `GET /api/ping` as a smoke test.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Follow the existing Flask blueprint style: route handlers use `snake_case`, role values use uppercase strings such as `STAFF`, `ADMIN`, and `CUSTOMER`, and JSON keys use lowercase underscores. Keep SQL parameterized with `%s` placeholders; never interpolate user input.

Prefer small route handlers and move shared behavior into `backend/common/`. Keep user-facing Vietnamese response messages consistent with the current API.

## Testing Guidelines

No automated test suite is currently committed. When adding tests, use `pytest` under `tests/`, mirroring backend modules, for example `tests/test_auth.py` or `tests/test_staff_transactions.py`. Cover successful requests, authorization failures, validation errors, and database rollback paths. Until tests exist, manually verify changed endpoints with local MySQL and `GET /api/ping`.

## Commit & Pull Request Guidelines

The current Git history has one short commit (`upload nmcnpm`), so use clear, imperative messages, for example `Add staff transaction approval tests` or `Fix auth import paths`.

Pull requests should include a concise summary, changed endpoints or schema objects, manual test steps, and screenshots or sample JSON responses when API behavior changes. Link related issues or coursework tasks when available.

## Security & Configuration Tips

Do not hard-code production secrets or database passwords. Keep local credentials out of commits and document required environment values when configuration is added. Review changes to `smart_savings.sql` carefully because it drops and recreates `modern_savings_db`.

## Agent-Specific Instructions

For Codex CLI work in this repository, prefix shell commands with `rtk`, for example `rtk pytest -q` or `rtk git status`, to follow the local token-optimized command policy.
