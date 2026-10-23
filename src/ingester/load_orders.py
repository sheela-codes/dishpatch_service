"""Load activity/orders.jsonl into the database (plain version: no validation, no logging).

Each line of the file is one order, written as JSON, with its dishes inside it:
    {"order_ref": "O-20260905-0001", "customer_ref": "C0051", ..., "items": [{"item_ref": "M0003", ...}]}

Steps:
  1. build lookup dictionaries: partner ref -> database id (one query each)
  2. read every order; skip orders already in the database
  3. insert all new orders                          (one executemany)
  4. look up the new orders' database ids           (one query)
  5. insert all their items into order_items        (one executemany)
"""
import json
from pathlib import Path

from src.ingester.load_restaurants import Result
from src.ingester.times import parse_timestamp

FILE = "activity/orders.jsonl"


def get_ids(conn, sql: str) -> dict:
    """Run a query that returns (ref, id) rows and give back {ref: id}."""
    ids = {}
    for ref, row_id in conn.execute(sql):
        ids[ref] = row_id
    return ids


SAVE_ORDER = """
    INSERT INTO public.orders
        (external_ref, customer_id, restaurant_id, driver_id, status,
         placed_at, accepted_at, picked_up_at, delivered_at, cancelled_at)
    VALUES
        (%(ref)s, %(customer_id)s, %(restaurant_id)s, %(driver_id)s, %(status)s::public.order_status,
         %(placed_at)s, %(accepted_at)s, %(picked_up_at)s, %(delivered_at)s, %(cancelled_at)s)
    ON CONFLICT (external_ref) DO NOTHING
"""
# %(status)s::public.order_status turns the text 'delivered' into the order_status type.

SAVE_ORDER_ITEM = """
    INSERT INTO public.order_items (order_id, menu_item_id, quantity, unit_price)
    VALUES (%(order_id)s, %(menu_item_id)s, %(quantity)s, %(unit_price)s)
    ON CONFLICT (order_id, menu_item_id) DO NOTHING
"""


def load_orders(conn, folder_path: Path, folder: str):
    """Load this folder's orders.jsonl. Runs inside the folder's transaction."""
    path = folder_path / FILE
    if not path.exists():
        return None

    # 1. Lookups: partner ref -> database id.
    customer_ids = get_ids(conn, "SELECT u.external_ref, u.id FROM public.users u "
                                 "JOIN public.accounts a ON a.id = u.account_id WHERE a.type = 'Customer'")
    driver_ids = get_ids(conn, "SELECT u.external_ref, u.id FROM public.users u "
                               "JOIN public.accounts a ON a.id = u.account_id WHERE a.type = 'Driver'")
    restaurant_ids = get_ids(conn, "SELECT external_ref, id FROM public.restaurants WHERE external_ref IS NOT NULL")
    item_ids = get_ids(conn, "SELECT external_ref, id FROM public.menu_items WHERE external_ref IS NOT NULL")
    existing_orders = get_ids(conn, "SELECT external_ref, id FROM public.orders WHERE external_ref IS NOT NULL")

    result = Result()
    orders_to_save = []
    items_by_order = {}          # {'O-20260905-0001': [ {item}, {item} ], ...}

    # 2. Read the file: one JSON object per line.
    with path.open(encoding="utf-8") as f:
        for line in f:
            order = json.loads(line)
            ref = order["order_ref"]
            if ref in existing_orders:
                continue         # already loaded on an earlier run

            driver_id = None
            if order["driver_ref"] is not None:          # cancelled orders have no driver
                driver_id = driver_ids[order["driver_ref"]]

            orders_to_save.append({
                "ref": ref,
                "customer_id": customer_ids[order["customer_ref"]],
                "restaurant_id": restaurant_ids[order["restaurant_ref"]],
                "driver_id": driver_id,
                "status": order["status"],
                "placed_at": parse_timestamp(order["placed_at"]),
                "accepted_at": parse_timestamp(order["accepted_at"]),
                "picked_up_at": parse_timestamp(order["picked_up_at"]),
                "delivered_at": parse_timestamp(order["delivered_at"]),
                "cancelled_at": parse_timestamp(order["cancelled_at"]),
            })
            items_by_order[ref] = order["items"]
            result.inserted += 1

    if len(orders_to_save) == 0:
        return result

    # 3. Insert all new orders.
    with conn.cursor() as cur:
        cur.executemany(SAVE_ORDER, orders_to_save)

    # 4. Their new database ids, in one query.
    new_refs = list(items_by_order.keys())
    order_ids = {}
    rows = conn.execute("SELECT external_ref, id FROM public.orders WHERE external_ref = ANY(%s)", [new_refs])
    for ref, order_id in rows:
        order_ids[ref] = order_id

    # 5. Insert every dish of every new order.
    items_to_save = []
    for ref in items_by_order:
        for item in items_by_order[ref]:
            items_to_save.append({
                "order_id": order_ids[ref],
                "menu_item_id": item_ids[item["item_ref"]],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            })
    with conn.cursor() as cur:
        cur.executemany(SAVE_ORDER_ITEM, items_to_save)

    return result
