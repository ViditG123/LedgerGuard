# LedgerGuard — Transaction Reconciliation API (MVP)

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
