# Healthcare Claims Analytics Platform

A personal portfolio project using synthetic healthcare data to build a local analytics pipeline and Power BI report.

## Business Goal
Organize healthcare claims data into reliable reporting tables for analyzing charges, payments, provider activity, and claim details.

## Technology
- Python: CSV ingestion and validation
- DuckDB: local analytical database
- SQL: staging and reporting transformations
- Power BI: interactive reporting
- Git and GitHub: version control

## Architecture
Synthea CSV files → DuckDB raw tables → staging tables → claim reporting table → validation and reconciliation → CSV export → Power BI

## Verified Results
- Loaded 18 CSV files.
- Processed 9,421 claims and 85,047 claim transactions.
- Passed 10 data quality checks.
- Reconciled charges and payments independently against source totals.
- Confirmed a $0.00 reconciliation difference for each total.

## Data Quality
Checks cover missing and duplicate IDs, unmatched claim references, missing or invalid dates, required financial amounts, and failed numeric conversions.

## Reporting Logic
- Reporting grain: one row per claim.
- Transactions are aggregated before joining to claims to prevent double counting.
- Charges use AMOUNT on CHARGE transactions.
- Payments use PAYMENTS on PAYMENT transactions.
- Transfers are excluded from charge and payment totals.
- Payments include insurer and patient payments.
- Dashboard trends use claim service dates, not payment receipt dates.

## Project Files
- scripts/ingest.py: load CSV files into raw tables
- scripts/staging.sql: clean and convert source fields
- scripts/validate.py: run data quality checks
- scripts/reporting.sql: build claim-level reporting
- scripts/reconcile.py: compare source and reporting totals
- scripts/export.py: validate and export reporting data

## Data Source
[Synthea by MITRE](https://synthetichealth.github.io/downloads.html)

Download the CSV sample and place the extracted CSV files in data/raw/.

All records are synthetic. No employer data or internal code is used.

## Current Limitations
- Uses a static sample dataset.
- Pipeline stages are currently run separately.
- No production scheduling or incremental change processing is implemented.
- Equal overall charges and payments do not establish that every claim is fully paid.
