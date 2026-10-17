from pathlib import Path
import duckdb

project = Path(__file__).resolve().parents[1]
raw_folder = project / "data" / "raw"
database = project / "data" / "warehouse" / "healthcare.duckdb"
database.parent.mkdir(parents=True, exist_ok=True)

files = sorted(raw_folder.glob("*.csv"))
if not files:
    raise FileNotFoundError(f"No CSV files found in {raw_folder}")

print(f"Found {len(files)} CSV files. Starting load...", flush=True)

connection = duckdb.connect(str(database))

try:
    connection.execute("CREATE SCHEMA IF NOT EXISTS raw").fetchall()
    connection.execute("BEGIN TRANSACTION").fetchall()

    try:
        for file in files:
            table = '"' + file.stem.replace('"', '""') + '"'
            path = str(file).replace("'", "''")
            reader = (
                f"read_csv('{path}', header=true, all_varchar=true)"
            )

            source_count = connection.execute(
                f"SELECT COUNT(*) FROM {reader}"
            ).fetchall()[0][0]

            connection.execute(
                f"CREATE OR REPLACE TABLE raw.{table} "
                f"AS SELECT * FROM {reader}"
            ).fetchall()

            loaded_count = connection.execute(
                f"SELECT COUNT(*) FROM raw.{table}"
            ).fetchall()[0][0]

            if source_count != loaded_count:
                raise ValueError(f"Row count mismatch: {file.name}")

            print(
                f"{file.name}: {loaded_count:,} rows verified",
                flush=True
            )

        connection.execute("COMMIT").fetchall()

    except Exception:
        connection.execute("ROLLBACK").fetchall()
        raise

finally:
    connection.close()

print(f"Load successful! Database: {database}")
