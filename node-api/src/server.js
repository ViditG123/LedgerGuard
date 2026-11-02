import express from "express";
import pg from "pg";
import { toCents, money } from "./ledger.js";

const app = express();
app.use(express.json({ limit: "32kb" }));
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL || "postgresql://postgres:postgres@localhost:5432/ledgerguard" });

async function initialize() {
  await pool.query(`CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    account TEXT NOT NULL,
    amount_cents BIGINT NOT NULL,
    memo TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`);
}
app.get("/health", (_req, res) => res.json({ status: "ok" }));
app.post("/transactions", async (req, res) => {
  try {
    const { account, amount, memo = "" } = req.body ?? {};
    if (typeof account !== "string" || !account.trim() || account.length > 100 || typeof memo !== "string" || memo.length > 500) {
      return res.status(422).json({ error: "Invalid account or memo" });
    }
    const cents = toCents(amount);
    const { rows } = await pool.query(
      "INSERT INTO transactions(account, amount_cents, memo) VALUES ($1,$2,$3) RETURNING id, account, amount_cents, memo",
      [account, cents, memo]
    );
    return res.status(201).json({ id: rows[0].id, account, amount: money(cents), memo });
  } catch (error) {
    if (error.message.startsWith("Amount")) return res.status(422).json({ error: error.message });
    console.error("Transaction insert failed", error);
    return res.status(500).json({ error: "Database unavailable" });
  }
});
app.get("/transactions", async (req, res) => {
  try {
    const account = req.query.account;
    const result = account
      ? await pool.query("SELECT * FROM transactions WHERE account=$1 ORDER BY id DESC LIMIT 200", [account])
      : await pool.query("SELECT * FROM transactions ORDER BY id DESC LIMIT 200");
    return res.json(result.rows.map(row => ({ id: row.id, account: row.account, amount: money(Number(row.amount_cents)), memo: row.memo, created_at: row.created_at })));
  } catch (error) {
    console.error("Transaction list failed", error);
    return res.status(500).json({ error: "Database unavailable" });
  }
});
app.get("/accounts/:account/balance", async (req, res) => {
  try {
    const { rows } = await pool.query("SELECT COALESCE(SUM(amount_cents),0) AS cents FROM transactions WHERE account=$1", [req.params.account]);
    return res.json({ account: req.params.account, balance: money(Number(rows[0].cents)) });
  } catch (error) {
    console.error("Balance query failed", error);
    return res.status(500).json({ error: "Database unavailable" });
  }
});
app.post("/reconcile", async (req, res) => {
  try {
    const { account, expected_balance } = req.body ?? {};
    if (typeof account !== "string" || !account.trim()) return res.status(422).json({ error: "Account required" });
    const expected = toCents(expected_balance);
    const { rows } = await pool.query("SELECT COALESCE(SUM(amount_cents),0) AS cents FROM transactions WHERE account=$1", [account]);
    const actual = Number(rows[0].cents);
    return res.json({ account, expected: money(expected), actual: money(actual), difference: money(actual - expected), matched: actual === expected });
  } catch (error) {
    if (error.message.startsWith("Amount")) return res.status(422).json({ error: error.message });
    console.error("Reconciliation failed", error);
    return res.status(500).json({ error: "Database unavailable" });
  }
});
const port = Number(process.env.PORT || 8001);
initialize().then(() => app.listen(port, () => console.log("LedgerGuard Node API listening on", port)))
  .catch(error => { console.error("Database initialization failed", error); process.exitCode = 1; pool.end(); });
