CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.claims AS
SELECT
    NULLIF(TRIM(Id), '') AS claim_id,
    NULLIF(TRIM(PATIENTID), '') AS patient_id,
    NULLIF(TRIM(PROVIDERID), '') AS provider_id,
    NULLIF(TRIM(PRIMARYPATIENTINSURANCEID), '') AS primary_payer_id,
    TRY_CAST(SERVICEDATE AS TIMESTAMPTZ) AS service_timestamp,
    UPPER(TRIM(STATUS1)) AS primary_status,
    TRY_CAST(OUTSTANDING1 AS DECIMAL(18,2)) AS primary_outstanding
FROM raw.claims;

CREATE OR REPLACE TABLE staging.claim_transactions AS
SELECT
    NULLIF(TRIM(ID), '') AS transaction_id,
    NULLIF(TRIM(CLAIMID), '') AS claim_id,
    NULLIF(TRIM(CHARGEID), '') AS charge_id,
    NULLIF(TRIM(PATIENTID), '') AS patient_id,
    NULLIF(TRIM(PROVIDERID), '') AS provider_id,
    UPPER(TRIM(TYPE)) AS transaction_type,
    TRY_CAST(FROMDATE AS TIMESTAMPTZ) AS transaction_timestamp,
    TRY_CAST(AMOUNT AS DECIMAL(18,2)) AS amount,
    TRY_CAST(PAYMENTS AS DECIMAL(18,2)) AS payments,
    TRY_CAST(ADJUSTMENTS AS DECIMAL(18,2)) AS adjustments,
    TRY_CAST(TRANSFERS AS DECIMAL(18,2)) AS transfers,
    TRY_CAST(OUTSTANDING AS DECIMAL(18,2)) AS outstanding
FROM raw.claims_transactions;
