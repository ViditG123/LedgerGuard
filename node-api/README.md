# LedgerGuard Node.js + PostgreSQL service

This is an **alternative backend** to the existing Python/SQLite demo API. It supports transaction creation, listing, account balances, and reconciliation with parameterized PostgreSQL queries.

## Run

From this directory:

```bash
docker compose up --build
```

API docs are not generated for this Express service. Test the health endpoint at http://localhost:8001/health.

Example:

```bash
curl -X POST http://localhost:8001/transactions -H "Content-Type: application/json" -d '{"account":"demo","amount":"100.00","memo":"synthetic"}'
```

The React frontend still proxies to the Python API on port 8000 by default. To use this service instead, change the target in `frontend/vite.config.ts` to `http://localhost:8001` and run the frontend. **The two backends have separate databases.**

This is a demo with no authentication or production security controls. Never use real financial records.
