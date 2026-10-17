from pathlib import Path
import duckdb

project = Path(__file__).resolve().parents[1]
database = project / "data" / "warehouse" / "healthcare.duckdb"

checks = {
    "Missing claim IDs": """
        SELECT COUNT(*) FROM staging.claims
        WHERE claim_id IS NULL
    """,
    "Duplicate claim IDs": """
        SELECT COUNT(*) FROM (
            SELECT claim_id FROM staging.claims
            GROUP BY claim_id HAVING COUNT(*) > 1
        )
    """,
    "Missing transaction IDs": """
        SELECT COUNT(*) FROM staging.claim_transactions
        WHERE transaction_id IS NULL
    """,
    "Duplicate transaction IDs": """
        SELECT COUNT(*) FROM (
            SELECT transaction_id FROM staging.claim_transactions
            GROUP BY transaction_id HAVING COUNT(*) > 1
        )
    """,
    "Transactions without a matching claim": """
        SELECT COUNT(*)
        FROM staging.claim_transactions t
        LEFT JOIN staging.claims c ON t.claim_id = c.claim_id
        WHERE c.claim_id IS NULL
    """,
    "Missing or invalid claim dates": """
        SELECT COUNT(*) FROM staging.claims
        WHERE service_timestamp IS NULL
    """,
    "Missing or invalid transaction dates": """
        SELECT COUNT(*) FROM staging.claim_transactions
        WHERE transaction_timestamp IS NULL
    """,
    "Charges missing a valid amount": """
        SELECT COUNT(*) FROM staging.claim_transactions
        WHERE transaction_type = 'CHARGE' AND amount IS NULL
    """,
    "Payments missing a valid payment amount": """
        SELECT COUNT(*) FROM staging.claim_transactions
        WHERE transaction_type = 'PAYMENT' AND payments IS NULL
    """,
    "Failed numeric conversions": """
        SELECT COUNT(*) FROM raw.claims_transactions
        WHERE
            (NULLIF(TRIM(AMOUNT), '') IS NOT NULL
             AND TRY_CAST(AMOUNT AS DECIMAL(18,2)) IS NULL)
         OR (NULLIF(TRIM(PAYMENTS), '') IS NOT NULL
             AND TRY_CAST(PAYMENTS AS DECIMAL(18,2)) IS NULL)
         OR (NULLIF(TRIM(ADJUSTMENTS), '') IS NOT NULL
             AND TRY_CAST(ADJUSTMENTS AS DECIMAL(18,2)) IS NULL)
         OR (NULLIF(TRIM(TRANSFERS), '') IS NOT NULL
             AND TRY_CAST(TRANSFERS AS DECIMAL(18,2)) IS NULL)
         OR (NULLIF(TRIM(OUTSTANDING), '') IS NOT NULL
             AND TRY_CAST(OUTSTANDING AS DECIMAL(18,2)) IS NULL)
    """,
}

failed = 0

with duckdb.connect(str(database), read_only=True) as connection:
    for name, sql in checks.items():
        count = connection.execute(sql).fetchall()[0][0]
        status = "PASS" if count == 0 else "FAIL"
        print(f"{status}: {name} — {count}")
        if count:
            failed += 1

print(f"\nChecks: {len(checks)} | Failed: {failed}")
raise SystemExit(1 if failed else 0)
