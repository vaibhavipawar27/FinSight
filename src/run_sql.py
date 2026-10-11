
import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

data_path = (
    ROOT / "data" / "processed" / "transactions_clean.csv"
).as_posix()

sql_path = ROOT / "sql" / "analysis.sql"

# Read the SQL file
sql_text = sql_path.read_text(encoding="utf-8")

# Run each query independently
queries = [
    q.strip()
    for q in sql_text.split(";")
    if q.strip()
]

connection = duckdb.connect()

for number, query in enumerate(queries, start=1):
    query = query.replace(
        "'data/processed/transactions_clean.csv'",
        f"'{data_path}'"
    )

    print(f"\n{'=' * 15} QUERY {number} {'=' * 15}")

    result = connection.execute(query).df()
    print(result.to_string(index=False))

connection.close()
