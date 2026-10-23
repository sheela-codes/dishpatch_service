"""Load reference/drivers.csv into the database (plain version: no validation, no logging).

A driver is a person: contacts -> profiles -> accounts (type 'Driver') -> users.
  - a new driver_ref: create the person (see people.py)
  - a known driver_ref: only update whether they're still active (e.g. a driver who left)
"""
import csv
from pathlib import Path

from src.ingester.load_restaurants import Result
from src.ingester.people import create_person

FILE = "reference/drivers.csv"


def get_existing_drivers(conn) -> dict:
    """{'D001': users.id, ...} for drivers already in the database."""
    drivers = {}
    rows = conn.execute(
        "SELECT u.external_ref, u.id FROM public.users u "
        "JOIN public.accounts a ON a.id = u.account_id WHERE a.type = 'Driver'"
    )
    for ref, user_id in rows:
        drivers[ref] = user_id
    return drivers


def load_drivers(conn, folder_path: Path, folder: str):
    """Load this folder's drivers.csv, if it has one. Runs inside the folder's transaction."""
    path = folder_path / FILE
    if not path.exists():
        return None

    existing = get_existing_drivers(conn)
    result = Result()

    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ref = row["driver_ref"]
            active = row["active"] == "true"

            if ref in existing:
                user_id = existing[ref]
                result.updated += 1
            else:
                user_id = create_person(
                    conn,
                    name=row["name"],
                    email=row["email"],
                    phone=row["phone"],
                    city=row["city"],
                    account_type="Driver",
                    external_ref=ref,
                )
                existing[ref] = user_id
                result.inserted += 1

            conn.execute("UPDATE public.users SET active = %s WHERE id = %s", [active, user_id])

    return result
