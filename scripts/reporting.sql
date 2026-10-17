CREATE SCHEMA IF NOT EXISTS reporting;

CREATE OR REPLACE TABLE reporting.claim_summary AS
WITH transaction_totals AS (
    SELECT
        claim_id,
        COUNT(*) AS transaction_count,
        SUM(
            CASE WHEN transaction_type = 'CHARGE'
                 THEN amount ELSE 0 END
        ) AS total_charges,
        SUM(
            CASE WHEN transaction_type = 'PAYMENT'
                 THEN payments ELSE 0 END
        ) AS total_payments,
        SUM(
            CASE WHEN transaction_type = 'ADJUSTMENT'
                 THEN adjustments ELSE 0 END
        ) AS total_adjustments
    FROM staging.claim_transactions
    GROUP BY claim_id
)
SELECT
    c.claim_id,
    c.patient_id,
    c.provider_id,
    c.primary_payer_id,
    CAST(c.service_timestamp AT TIME ZONE 'UTC' AS DATE) AS service_date,
    c.primary_status,
    c.primary_outstanding,
    COALESCE(t.transaction_count, 0) AS transaction_count,
    COALESCE(t.total_charges, 0) AS total_charges,
    COALESCE(t.total_payments, 0) AS total_payments,
    COALESCE(t.total_adjustments, 0) AS total_adjustments
FROM staging.claims c
LEFT JOIN transaction_totals t ON c.claim_id = t.claim_id;
