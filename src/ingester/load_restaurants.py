"""Load reference/restaurants.csv into the database (plain version: no validation, no logging).

For each row in the file:
  - a new restaurant: find its owner by email, or create the owner
  - a known restaurant: keep its current owner
Then save all rows in one go: a new restaurant_ref is inserted, a known one is updated.

The partner's files are assumed to be correct. A bad row (e.g. an unknown cuisine) will raise
an error, and the whole folder is rolled back.
"""
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from src.ingester.people import create_person, users_by_email

FILE = "reference/restaurants.csv"


@dataclass
class Result:
    """What happened to this file. __main__ uses these numbers for its summary and the load log."""
    inserted: int = 0
    updated: int = 0
    rejected: int = 0      # always 0 in this version (nothing is checked)

    @property
    def loaded(self) -> int:
        return self.inserted + self.updated


# --- lookups: one query each, done once per file -------------------------------------

def get_cuisine_ids(conn) -> dict:
    """{'Mexican': 7, 'Thai': 8, ...}"""
    cuisine_ids = {}
    rows = conn.execute("SELECT name, id FROM public.cuisines")
    for name, cuisine_id in rows:
        cuisine_ids[name] = cuisine_id
    return cuisine_ids


def get_existing_restaurants(conn) -> dict:
    """Restaurants already in the database: {'R001': owner's users.id, ...}"""
    existing = {}
    rows = conn.execute(
        "SELECT external_ref, user_id FROM public.restaurants WHERE external_ref IS NOT NULL"
    )
    for ref, user_id in rows:
        existing[ref] = user_id
    return existing


# --- owners --------------------------------------------------------------------------

def find_or_create_owner(conn, row: dict, owners: dict) -> int:
    """The owner's users.id: reuse the account with this email, or create a new person."""
    email = row["owner_email"]
    if email in owners:
        return owners[email]

    user_id = create_person(
        conn,
        name=row["owner_name"],
        email=email,
        phone=row["owner_phone"],
        city=row["city"],
        account_type="Restaurant",
    )
    owners[email] = user_id      # a second restaurant with the same owner reuses it
    return user_id


# --- saving --------------------------------------------------------------------------

SAVE_RESTAURANT = """
    INSERT INTO public.restaurants
        (external_ref, name, operational, user_id, cuisine_id, city, opened_at)
    VALUES
        (%(ref)s, %(name)s, %(active)s, %(user_id)s, %(cuisine_id)s, %(city)s, %(opened_at)s)
    ON CONFLICT (external_ref) DO UPDATE SET
        name        = EXCLUDED.name,
        operational = EXCLUDED.operational,
        cuisine_id  = EXCLUDED.cuisine_id,
        city        = EXCLUDED.city,
        opened_at   = EXCLUDED.opened_at
"""
# %(ref)s means "the value under the key 'ref' in each dictionary".
# EXCLUDED is the row we tried to insert; on a conflict its values replace the old ones.
# user_id is not in the UPDATE list, so an update never changes the owner.


# --- the loader ----------------------------------------------------------------------

def load_restaurants(conn, folder_path: Path, folder: str):
    """Load this folder's restaurants.csv, if it has one. Runs inside the folder's transaction."""
    path = folder_path / FILE
    if not path.exists():
        return None      # normal: reference files only appear when something changed

    cuisine_ids = get_cuisine_ids(conn)
    existing = get_existing_restaurants(conn)
    owners = users_by_email(conn)
    result = Result()

    to_save = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):          # each row is a dictionary: {'restaurant_ref': 'R001', ...}
            ref = row["restaurant_ref"]

            if ref in existing:
                user_id = existing[ref]          # known restaurant: keep its owner
                result.updated += 1
            else:
                user_id = find_or_create_owner(conn, row, owners)
                result.inserted += 1

            restaurant = {
                "ref": ref,
                "name": row["name"],
                "active": row["active"] == "true",                 # the text 'true' -> True
                "user_id": user_id,
                "cuisine_id": cuisine_ids[row["cuisine"]],         # 'Mexican' -> 7
                "city": row["city"],
                "opened_at": date.fromisoformat(row["opened_at"]), # '2021-05-14' -> a date
            }
            to_save.append(restaurant)

    with conn.cursor() as cur:
        cur.executemany(SAVE_RESTAURANT, to_save)   # insert or update all of them at once

    return result
