from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg


MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


def normalize_database_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def main() -> int:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        print("DATABASE_URL_NOT_CONFIGURED", file=sys.stderr)
        return 2

    scripts = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not scripts:
        print("NO_MIGRATIONS_FOUND", file=sys.stderr)
        return 3

    with psycopg.connect(normalize_database_url(database_url)) as connection:
        with connection.cursor() as cursor:
            for script in scripts:
                cursor.execute(script.read_text(encoding="utf-8"))
                print(f"migration_applied={script.name}")
        connection.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
