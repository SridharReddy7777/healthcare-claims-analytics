from pathlib import Path
import subprocess
import sys
import duckdb

project = Path(__file__).resolve().parents[1]

# Stop the export if either check fails.
for script in ["validate.py", "reconcile.py"]:
    subprocess.run(
        [sys.executable, str(project / "scripts" / script)],
        check=True,
        cwd=project,
    )

export_folder = project / "data" / "exports"
export_folder.mkdir(parents=True, exist_ok=True)
output = export_folder / "claim_summary.csv"
temporary = export_folder / "claim_summary.tmp.csv"

with duckdb.connect(
    str(project / "data" / "warehouse" / "healthcare.duckdb"),
    read_only=True,
) as connection:
    destination = str(temporary).replace("'", "''")
    connection.execute(f"""
        COPY (
            SELECT *
            FROM reporting.claim_summary
            ORDER BY service_date, claim_id
        )
        TO '{destination}' (HEADER, DELIMITER ',')
    """).fetchall()

temporary.replace(output)
print(f"\nExport successful: {output}")
