"""
Migrate data from local SQLite (gunpla.db) to Postgres.

Usage (PowerShell):
  $env:POSTGRES_URL="postgresql://user:pass@host:port/db"
  $env:SQLITE_PATH="C:\\path\\to\\gunpla.db"  # optional
  py scripts/migrations/sqlite_to_postgres.py
"""
import os
from sqlalchemy import create_engine, text
from flask import Flask

from models import db, Gunpla, Wishlist, Collection, Coupon, PriceHistory, User, ShareLink


TABLE_ORDER = [
    ("users", User),
    ("gunpla", Gunpla),
    ("coupons", Coupon),
    ("price_history", PriceHistory),
    ("wishlist", Wishlist),
    ("collection", Collection),
    ("share_links", ShareLink),
]


def _normalize_postgres_url(url: str) -> str:
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _get_sqlite_url():
    sqlite_path = os.environ.get("SQLITE_PATH") or os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "gunpla.db"
    )
    sqlite_path = os.path.abspath(sqlite_path)
    return f"sqlite:///{sqlite_path}"


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return result is not None


def _load_rows(sqlite_conn, table_name: str):
    result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
    return [dict(row._mapping) for row in result]


def _set_postgres_sequence(session, table_name: str):
    session.execute(
        text(
            "SELECT setval(pg_get_serial_sequence(:table, 'id'), "
            "COALESCE(MAX(id), 1), true) FROM " + table_name
        ),
        {"table": table_name},
    )


def main():
    postgres_url = _normalize_postgres_url(
        os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    )
    if not postgres_url:
        raise SystemExit("POSTGRES_URL/DATABASE_URL is required.")

    sqlite_url = _get_sqlite_url()
    sqlite_engine = create_engine(sqlite_url)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = postgres_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

        with sqlite_engine.connect() as sqlite_conn:
            for table_name, model in TABLE_ORDER:
                if not _table_exists(sqlite_conn, table_name):
                    print(f"[skip] table not found: {table_name}")
                    continue

                rows = _load_rows(sqlite_conn, table_name)
                if not rows:
                    print(f"[empty] {table_name}")
                    continue

                db.session.bulk_insert_mappings(model, rows)
                db.session.commit()
                print(f"[ok] {table_name}: {len(rows)} rows")

        if postgres_url.startswith("postgresql://"):
            for table_name, _ in TABLE_ORDER:
                db.session.execute(
                    text("SELECT 1 FROM pg_class WHERE relname=:name"),
                    {"name": table_name},
                )
                _set_postgres_sequence(db.session, table_name)
            db.session.commit()

    print("Migration completed.")


if __name__ == "__main__":
    main()
