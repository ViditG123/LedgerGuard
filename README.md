# LedgerGuard : Transaction Reconciliation API (MVP)

A synthetic transaction ledger implemented with FastAPI and SQLite. Stores amounts in integer cents and supports account balance calculations and reconciliation.

> **Scope:** This is a demonstration API, **not a banking service**. React, Node.js, PostgreSQL, Playwright and data pipelines are future work.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

1. POST `/transactions`: `{"account":"demo","amount":"100.00","memo":"credit"}`
2. POST `/transactions`: `{"account":"demo","amount":"-15.25","memo":"debit"}`
3. GET `/accounts/demo/balance`: balance is `84.75`
4. POST `/reconcile`: `{"account":"demo","expected_balance":"84.75"}`

## Docker and tests

```bash
docker compose up --build
python -m pytest -q
```

## Roadmap

- [ ] React/TypeScript financial operations dashboard
- [ ] PostgreSQL and Node.js migration
- [ ] Python/SQL reconciliation ETL and exception reporting
- [ ] Playwright E2E tests and CI

Use only synthetic financial data. This demo has no production authentication or banking-grade security.

## React dashboard and browser test

Start the Python API on port 8000. In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend can create synthetic transactions, show balances, and compare expected versus actual balances.

Run the Playwright UI smoke test with `cd frontend && npx playwright install chromium && npm test`. The test checks that the dashboard renders; it does **not** yet verify a complete financial transaction workflow. A Python reconciliation report and SQL aggregation query are available in `analytics/`.

## Node.js / PostgreSQL backend

An alternative Express + PostgreSQL service is now available under [node-api](node-api/README.md). It provides transaction creation, history, balance lookup and reconciliation with parameterized SQL. Start it with `cd node-api && docker compose up --build`. The React frontend still targets the Python API by default, so the Node service is not yet the default full-stack path. The Node and Python services use separate databases.

The Node service includes unit tests and a GitHub Actions workflow. PostgreSQL integration tests, authenticated financial workflows and comprehensive Playwright end-to-end tests remain future work.
