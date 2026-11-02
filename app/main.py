"""Synthetic transaction ledger and reconciliation API."""
import os
import sqlite3
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_PATH = os.getenv("LEDGERGUARD_DB", "ledgerguard.db")
app = FastAPI(title="LedgerGuard", version="0.1.0")

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, account TEXT NOT NULL, amount_cents INTEGER NOT NULL, memo TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")

class Transaction(BaseModel):
    account: str = Field(min_length=1, max_length=100)
    amount: str
    memo: str = Field(default="", max_length=500)

class ReconcileRequest(BaseModel):
    account: str = Field(min_length=1)
    expected_balance: str

def to_cents(amount: str) -> int:
    try:
        value = Decimal(amount)
    except InvalidOperation:
        raise ValueError("Amount must be a decimal string")
    if not value.is_finite() or value.as_tuple().exponent < -2:
        raise ValueError("Amount must have at most two decimal places")
    cents = value * 100
    if abs(cents) > 10**12:
        raise ValueError("Amount out of range")
    return int(cents)

def format_cents(cents: int) -> str:
    return f"{Decimal(cents) / 100:.2f}"

@app.on_event("startup")
def startup():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/transactions", status_code=201)
def add_transaction(req: Transaction):
    try:
        cents = to_cents(req.amount)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    with db() as conn:
        cursor = conn.execute("INSERT INTO transactions (account, amount_cents, memo) VALUES (?,?,?)", (req.account, cents, req.memo))
        transaction_id = cursor.lastrowid
    return {"id": transaction_id, "account": req.account, "amount": format_cents(cents), "memo": req.memo}

@app.get("/transactions")
def list_transactions(account: str | None = None):
    with db() as conn:
        if account:
            rows = conn.execute("SELECT * FROM transactions WHERE account=? ORDER BY id", (account,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM transactions ORDER BY id").fetchall()
    return [{"id": row["id"], "account": row["account"], "amount": format_cents(row["amount_cents"]), "memo": row["memo"], "created_at": row["created_at"]} for row in rows]

@app.get("/accounts/{account}/balance")
def balance(account: str):
    with db() as conn:
        cents = conn.execute("SELECT COALESCE(SUM(amount_cents),0) FROM transactions WHERE account=?", (account,)).fetchone()[0]
    return {"account": account, "balance": format_cents(cents)}

@app.post("/reconcile")
def reconcile(req: ReconcileRequest):
    try:
        expected = to_cents(req.expected_balance)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    with db() as conn:
        actual = conn.execute("SELECT COALESCE(SUM(amount_cents),0) FROM transactions WHERE account=?", (req.account,)).fetchone()[0]
    return {"account": req.account, "expected": format_cents(expected), "actual": format_cents(actual), "difference": format_cents(actual - expected), "matched": actual == expected}
