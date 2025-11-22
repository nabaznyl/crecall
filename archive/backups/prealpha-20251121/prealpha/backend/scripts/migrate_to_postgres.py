"""Data migration utility: migrate existing SQLite data to PostgreSQL.

Usage:
    python backend/scripts/migrate_to_postgres.py \
        --sqlite sqlite:///crecall.db \
        --postgres postgresql+psycopg2://user:pass@host:5432/crecall

Requires psycopg2 installed for PostgreSQL driver.
"""
import argparse
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

TABLES = ["sessions", "clips", "checkpoints", "memories"]


def copy_table(src_conn, dst_conn, table: str):
    src_rows = src_conn.execute(text(f"SELECT * FROM {table}")).fetchall()
    if not src_rows:
        return 0

    # Check destination existing rows to avoid duplicates
    existing = dst_conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    if existing:
        print(f"Skipping {table}: destination already has {existing} rows")
        return 0

    # Build insert statement dynamically
    cols = src_rows[0].keys()
    placeholders = ", ".join([f":{c}" for c in cols])
    insert_sql = text(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})")
    for row in src_rows:
        dst_conn.execute(insert_sql, dict(row))
    return len(src_rows)


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument("--sqlite", required=True, help="SQLite URL (e.g. sqlite:///crecall.db)")
    parser.add_argument("--postgres", required=True, help="PostgreSQL URL (e.g. postgresql+psycopg2://user:pass@host/db)")
    args = parser.parse_args()

    try:
        src_engine = create_engine(args.sqlite)
        dst_engine = create_engine(args.postgres)
    except SQLAlchemyError as e:
        print(f"Engine creation failed: {e}")
        sys.exit(1)

    with src_engine.connect() as src_conn, dst_engine.connect() as dst_conn:
        migrated_total = 0
        for table in TABLES:
            try:
                count = copy_table(src_conn, dst_conn, table)
                migrated_total += count
                if count:
                    print(f"Migrated {count} rows from {table}")
            except SQLAlchemyError as e:
                print(f"Error migrating {table}: {e}")
        dst_conn.commit()
        print(f"Migration complete. Total rows migrated: {migrated_total}")

if __name__ == "__main__":
    main()
