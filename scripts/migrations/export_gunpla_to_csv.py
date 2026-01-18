"""
Export Gunpla data from SQLite to CSV for seeding.

Usage (PowerShell):
  py scripts/migrations/export_gunpla_to_csv.py
"""
import csv
import os
from sqlalchemy import create_engine, text


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sqlite_path = os.path.join(base_dir, "gunpla.db")
    if not os.path.exists(sqlite_path):
        raise SystemExit(f"SQLite not found: {sqlite_path}")

    output_path = os.path.join(base_dir, "data", "seed_gunpla.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    engine = create_engine(f"sqlite:///{sqlite_path}")
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM gunpla")).fetchall()

    if not rows:
        raise SystemExit("No gunpla rows found.")

    columns = rows[0]._mapping.keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row._mapping[col] for col in columns])

    print(f"Exported {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
