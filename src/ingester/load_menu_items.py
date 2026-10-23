from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple
from dataclasses import dataclass

from src.ingester.csvfile import last_one_wins
from src.ingester import logs, validate
import csv
from pathlib import Path

@dataclass
class Result:
    """What happened to this file. __main__ uses these numbers for its summary and the load log."""
    inserted: int = 0
    updated: int = 0
    rejected: int = 0      # always 0 in this version (nothing is checked)

    @property
    def loaded(self) -> int:
        return self.inserted + self.updated

FILE = "reference/menu_items.csv"


SAVE_MENU_ITEM= """
    INSERT INTO public.menu_items
        (external_ref, name, price, restaurant_id, active)
    VALUES
        (%(external_ref)s, %(name)s, %(price)s, %(restaurant_id)s, %(active)s)
    ON CONFLICT (external_ref) DO UPDATE SET
        name           = EXCLUDED.name,
        price          = EXCLUDED.price,
        restaurant_id  = EXCLUDED.restaurant_id,
        active         = EXCLUDED.active
"""


def get_existing(conn) -> dict:
    """MenuItems already in the database"""
    existing = []
    rows = conn.execute(
        "SELECT external_ref FROM public.menu_items WHERE external_ref IS NOT NULL"
    )
    for (external_ref,) in rows: # One value tuple -- ('M0059',) → external_ref = 'M0059'
        existing.append(external_ref)
    return existing

def get_existing_restaurant_id(conn) -> dict:
    """MenuItems already in the database"""
    existing = {}
    rows = conn.execute(
        "SELECT external_ref, id FROM public.restaurants WHERE external_ref IS NOT NULL"
    )
    for ref, restaurant_id in rows:
        existing[ref] = restaurant_id
    return existing
   

def load_menu_items(conn, folder_path: Path, folder: str):
    result = Result() 
    path = folder_path / FILE
    to_save = []
    existing = get_existing(conn)
    res_ids = get_existing_restaurant_id(conn)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):          # each row is a dictionary: {'restaurant_ref': 'R001', ...}
            ref = row["item_ref"]

            if ref in existing:
                result.updated += 1
            else:
                result.inserted += 1

            res_id = res_ids[row["restaurant_ref"]]
            menu_item = {
                "external_ref": ref,
                "restaurant_id": res_id,
                "name": row["name"],
                "price": row["price"],
                "active": row["active"] == "true",                
            }
            to_save.append(menu_item)


    with conn.cursor() as cur:
        cur.executemany(SAVE_MENU_ITEM, to_save)   # insert or update all of them at once 
    return result            