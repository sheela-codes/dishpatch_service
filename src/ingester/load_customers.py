"""Load activity/customers.csv into the database (plain version: no validation, no logging).

A customer is a person: contacts -> profiles -> accounts (type 'Customer') -> users.
Customers are activity: a customer_ref that's already in the database is skipped.
"""
import csv
from pathlib import Path

from src.ingester.load_restaurants import Result
from src.ingester.people import create_person
from src.ingester.times import parse_timestamp

FILE = "activity/customers.csv"


def get_existing_customer_refs(conn) -> set:
    """The customer refs already in the database, e.g. {'C0001', 'C0002', ...}."""
    refs = set()
    rows = conn.execute(
        "SELECT u.external_ref FROM public.users u "
        "JOIN public.accounts a ON a.id = u.account_id WHERE a.type = 'Customer'"
    )
    for (ref,) in rows:
        refs.add(ref)
    return refs


def load_customers(conn, folder_path: Path, folder: str):
    """Load this folder's customers.csv. Runs inside the folder's transaction."""
    path = folder_path / FILE
    if not path.exists():
        return None

    existing = get_existing_customer_refs(conn)
    result = Result()

    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ref = row["customer_ref"]
            if ref in existing:
                continue                     # already loaded on an earlier day

            create_person(
                conn,
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                city=row["city"],
                address=row["address"],
                account_type="Customer",
                external_ref=ref,
                created_at=parse_timestamp(row["signed_up_at"]),   # when they signed up
            )
            existing.add(ref)
            result.inserted += 1

    return result
