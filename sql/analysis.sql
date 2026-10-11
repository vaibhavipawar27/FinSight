
-- QUERY 1: Overall transaction KPIs
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'success')
        / COUNT(*), 2
    ) AS success_rate_pct,
    ROUND(
        SUM(amount) FILTER (WHERE status = 'success'), 2
    ) AS successful_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM read_csv_auto(
    'data/processed/transactions_clean.csv'
);


-- QUERY 2: Transaction status breakdown
SELECT
    status,
    COUNT(*) AS transaction_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
    ) AS percentage
FROM read_csv_auto(
    'data/processed/transactions_clean.csv'
)
GROUP BY status
ORDER BY transaction_count DESC;


-- QUERY 3: Daily transaction trends
SELECT
    CAST(transaction_date AS DATE) AS transaction_day,
    COUNT(*) AS total_transactions,
    COUNT(*) FILTER (
        WHERE status = 'success'
    ) AS successful_transactions,
    ROUND(
        SUM(amount) FILTER (WHERE status = 'success'), 2
    ) AS successful_value
FROM read_csv_auto(
    'data/processed/transactions_clean.csv'
)
GROUP BY CAST(transaction_date AS DATE)
ORDER BY transaction_day;


-- QUERY 4: Performance by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(
        SUM(amount) FILTER (WHERE status = 'success'), 2
    ) AS successful_value,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'success')
        / COUNT(*), 2
    ) AS success_rate_pct
FROM read_csv_auto(
    'data/processed/transactions_clean.csv'
)
GROUP BY transaction_type
ORDER BY successful_value DESC;


-- QUERY 5: Performance by channel
SELECT
    channel,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed_transactions,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'failed')
        / COUNT(*), 2
    ) AS failure_rate_pct,
    ROUND(
        SUM(amount) FILTER (WHERE status = 'success'), 2
    ) AS successful_value
FROM read_csv_auto(
    'data/processed/transactions_clean.csv'
)
GROUP BY channel
ORDER BY failure_rate_pct DESC;
