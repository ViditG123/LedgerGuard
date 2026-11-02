"""Read-only account reconciliation report using the local SQLite demo database."""
import argparse
import sqlite3
from decimal import Decimal

def account_balances(path: str) -> list[tuple[str, str]]:
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT account, SUM(amount_cents) FROM transactions GROUP BY account ORDER BY account"
        ).fetchall()
    return [(account, f"{Decimal(cents) / 100:.2f}") for account, cents in rows]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="ledgerguard.db")
    args = parser.parse_args()
    for account, amount in account_balances(args.db):
        print(f"{account}: {amount}")
