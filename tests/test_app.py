import os
import tempfile
from fastapi.testclient import TestClient
from app import main

def test_transactions_and_reconciliation():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "test.db")
        with TestClient(main.app) as client:
            assert client.post("/transactions", json={"account": "demo", "amount": "100.00", "memo": "credit"}).status_code == 201
            assert client.post("/transactions", json={"account": "demo", "amount": "-15.25", "memo": "debit"}).status_code == 201
            assert client.get("/accounts/demo/balance").json()["balance"] == "84.75"
            assert client.post("/reconcile", json={"account": "demo", "expected_balance": "84.75"}).json()["matched"] is True

def test_reject_invalid_amount():
    with tempfile.TemporaryDirectory() as tmp:
        main.DB_PATH = os.path.join(tmp, "test.db")
        with TestClient(main.app) as client:
            assert client.post("/transactions", json={"account": "demo", "amount": "1.234"}).status_code == 422
