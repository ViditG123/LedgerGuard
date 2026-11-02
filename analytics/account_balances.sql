-- Aggregate synthetic transaction balances by account.
SELECT
    account,
    COUNT(*) AS transaction_count,
    SUM(amount_cents) AS balance_cents
FROM transactions
GROUP BY account
ORDER BY account;
