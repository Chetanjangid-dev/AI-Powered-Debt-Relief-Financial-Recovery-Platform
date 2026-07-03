# Contributing

No `CONTRIBUTING.md`, code-of-conduct, or PR template exists in the uploaded project. The guidelines below are proposed conventions based on the codebase's existing (inconsistent) patterns, intended to bring consistency going forward.

## Before you start

Read [Troubleshooting.md](Troubleshooting.md) first — several things that look like bugs (duplicate scoring engines, static alias endpoints, empty `security.py`) are known, documented gaps rather than things to silently "fix" without awareness of their full scope.

## Branch / commit conventions

None are enforced in the repo (no `.github/`, no commit-lint config). Suggested minimum:
- `feature/<short-description>`, `fix/<short-description>` branch naming.
- Conventional Commits style (`feat:`, `fix:`, `docs:`, `refactor:`) for commit messages, to make future changelog generation possible.

## Code style

- **Backend (Python)**: The existing code follows a consistent-enough style (docstrings on every function, type hints on function signatures, `snake_case`). No linter/formatter config (`ruff`, `black`, `flake8`) is present in the repo — recommend adding `black` + `ruff` and a pre-commit hook.
- **Frontend (JS/JSX)**: `eslint.config.js` is present and does run (`npm run lint`), using `@eslint/js`, `eslint-plugin-react-hooks`, and `eslint-plugin-react-refresh`. Run `npm run lint` before submitting frontend changes.

## Before submitting a change

1. **Backend**: there is no test suite in the repository (no `pytest`, no `tests/` folder). If you add backend logic, especially to `financial_engine.py` or `calculator.py` (pure functions, easy to unit test), please add tests — see [Future_Improvements.md](Future_Improvements.md) for suggested test-coverage priorities.
2. **Frontend**: no test runner (`vitest`, `jest`) is configured. Manual verification against `npm run dev` is the only current path.
3. Run `npm run build` to confirm the frontend still builds cleanly.
4. If you touch anything under `DataBase/`, remember it is imported by **both** by-path-string references throughout `Backend/app/api/*.py` — grep for `sys.path.insert` and `import crud`/`import models`/`import schemas` to find every place that needs to stay in sync.

## Areas that most need contributions

See [Future_Improvements.md](Future_Improvements.md) for the full prioritized list. Highest-value, lowest-risk starting points:
- Add automated tests for `financial_engine.py`/`calculator.py` (pure math, no I/O — easy first PR).
- Reconcile the two settlement-scoring engines into one.
- Wire the Dashboard/History pages to real data instead of static aliases.
- Move the hard-coded JWT secret to an environment variable.

## Reporting issues

No issue template exists. When filing an issue, please include: which endpoint/page is affected, whether you hit the versioned API (`/api/v1/...`) or an alias endpoint (`/api/...`), and your `GET /api/v1/ai/status` response if the issue involves AI-generated content.
