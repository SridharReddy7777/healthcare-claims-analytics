from pathlib import Path
from decimal import Decimal
import duckdb

project = Path(__file__).resolve().parents[1]
database = project / "data" / "warehouse" / "healthcare.duckdb"

with duckdb.connect(str(database), read_only=True) as connection:
    source = connection.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN TYPE = 'CHARGE'
                THEN CAST(AMOUNT AS DECIMAL(18,2)) ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN TYPE = 'PAYMENT'
                THEN CAST(PAYMENTS AS DECIMAL(18,2)) ELSE 0 END), 0)
        FROM raw.claims_transactions
    """).fetchall()[0]

    reporting = connection.execute("""
        SELECT
            COALESCE(SUM(total_charges), 0),
            COALESCE(SUM(total_payments), 0)
        FROM reporting.claim_summary
    """).fetchall()[0]

    failed = False

    for label, raw_total, report_total in zip(
        ["Charges", "Payments"], source, reporting
    ):
        difference = raw_total - report_total
        passed = difference == Decimal("0")
        print(
            f"{'PASS' if passed else 'FAIL'}: {label} | "
            f"Source: {raw_total:,.2f} | "
            f"Reporting: {report_total:,.2f} | "
            f"Difference: {difference:,.2f}"
        )
        if not passed:
            failed = True

raise SystemExit(1 if failed else 0)
