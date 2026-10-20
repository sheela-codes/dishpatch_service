# Ingester requirements

The ingester reads the partner's delivery folders (format described in `provider.md`),
validates every record, and loads the valid ones into Postgres. It must be **safe to re-run**.

- Run: `python -m src.scripts.ingester --in data/incoming/redmondtownservice`
- Runs inside the `api` container: `docker compose exec api python -m src.scripts.ingester ...`

## 1. Finding work

1. Find every `YYYY/MM/DD` folder under the partner folder.
2. Process them **oldest first** (later days depend on earlier ones).
3. Skip a folder that has no `_DONE` file (log INFO: not complete yet).
4. Skip a folder whose files are already in the load log with the same checksum (log INFO: already loaded).
5. If a file is in the load log with a **different** checksum, stop with an ERROR
   (the partner changed a delivered file; a human must decide).

## 2. Processing order inside one folder

```
1. reference/restaurants.csv    (creates owner users too)
2. reference/menu_items.csv
3. reference/drivers.csv
4. activity/customers.csv
5. build lookup dictionaries     (see section 4)
6. activity/orders.jsonl         (orders and their items)
7. write load-log rows
8. COMMIT
```

Missing reference files are normal (nothing changed that day).

## 3. Transactions

- **One transaction per folder.** Steps 1–7 above run in a single transaction.
- Invalid **data** (a bad row) is rejected and logged; it does **not** abort the transaction.
- An unexpected **error** (bug, lost connection) rolls back the whole folder, logs an ERROR,
  and stops the run. Nothing from that folder is saved; re-running starts it fresh.
- A transaction sees its own uncommitted inserts, so step 5 sees rows from steps 1–4.

## 4. Lookups: dictionaries, no N+1 queries

Never run a SELECT per row. After steps 1–4, build these dictionaries **once per folder**,
one query each:

| Dictionary | Maps | Source |
|---|---|---|
| `restaurants_ref` | `R007` → (restaurant id, active) | `restaurants` |
| `customers_ref` | `C0042` → user id | `users` joined to `accounts`, `type = 'Customer'` |
| `drivers_ref` | `D003` → (user id, active) | `users` joined to `accounts`, `type = 'Driver'` |
| `items_ref` | `M0071` → (item id, restaurant id, price, active) | `menu_items` |

- Customers and drivers are both in `users`; filtering on the account type stops a driver's
  ref being accepted as a customer.
- Validation of orders then only uses dictionary lookups (`ref in dict`).
- After inserting orders, build `orders_ref` (`O-...` → order id) with **one** query
  (`WHERE external_ref = ANY(%s)`) to insert the order items.
- Inserts are batched with `cursor.executemany(...)`, not one call per row.

## 5. Mapping files to tables

| File | Tables written |
|---|---|
| restaurants.csv | owner: `contacts` → `profiles` → `accounts` (type `Restaurant`) → `users`; then `restaurants` (cuisine looked up by name in `cuisines`) |
| menu_items.csv | `menu_items` |
| drivers.csv | `contacts` → `profiles` → `accounts` (type `Driver`) → `users` |
| customers.csv | `contacts` → `profiles` → `accounts` (type `Customer`) → `users` |
| orders.jsonl | `orders`, `order_items` |

- `accounts.username` = email. Imported accounts get a placeholder password (they cannot log in).
- `restaurants.operational` = the file's `active`.

## 6. Idempotency (safe to re-run)

Three layers:

1. **Transaction per folder**: a failed load leaves nothing behind.
2. **Unique partner refs**: `external_ref text UNIQUE` on `restaurants`, `menu_items`, `users`, `orders`.
   - Reference files (restaurants, menu items, drivers): `ON CONFLICT (external_ref) DO UPDATE`
     (a known ref means "update it").
   - Activity (customers, orders): `ON CONFLICT (external_ref) DO NOTHING`
     (a row already loaded on an earlier day is kept as it was).
   - `order_items`: `ON CONFLICT (order_id, menu_item_id) DO NOTHING`.
3. **Load log** table, written in the same transaction as the data:

   ```sql
   CREATE TABLE public.file_loads (
       folder        text NOT NULL,          -- '2026/10/19'
       file_name     text NOT NULL,          -- 'activity/orders.jsonl'
       checksum      text NOT NULL,          -- SHA-256 of the file
       rows_loaded   integer NOT NULL,
       rows_rejected integer NOT NULL,
       loaded_at     timestamptz NOT NULL DEFAULT now(),
       PRIMARY KEY (folder, file_name)
   );
   ```

## 7. Validation

A record that fails any check is **rejected**: skipped, and logged with the reason.

### 7.1 File level
- A CSV that can't be read, or whose header doesn't match the spec: reject the **whole file**
  (ERROR). Rows in later files that depend on it are then rejected as unknown refs.
- A CSV row with the wrong number of columns: reject the row.
- An `orders.jsonl` line that isn't valid JSON: reject that line (one order).

### 7.2 Field level

Required fields: all fields, **except** `driver_ref`, `accepted_at`, `picked_up_at`,
`delivered_at`, `cancelled_at`. Empty or missing required field → reject.

Allowed characters are defined **per field** (no single "no special characters" rule):

| Field | Rule |
|---|---|
| refs | exact pattern from `provider.md` (e.g. `^R\d{3}$`) |
| names, cities | letters, spaces, `'` and `-` |
| address | letters, digits, spaces and `, . # ' -` |
| email | `something@something.something`, no spaces |
| phone | `^\d{10}$` |
| timestamps | `YYYY-MM-DDTHH:MM:SS.sssZ` and a real date/time |
| dates | `YYYY-MM-DD` and a real date |
| price, unit_price | number with up to 2 decimals, 0.10 to 100.00 |
| quantity | whole number, at least 1 |
| status | one of the 6 order statuses |
| cuisine | one of the names in the `cuisines` table |
| active | `true` or `false` |

### 7.3 Reference checks (using the dictionaries)
- `menu_items.restaurant_ref` exists.
- Order `restaurant_ref` exists and is active.
- Order `customer_ref` exists and is a customer.
- Order `driver_ref`, if given, exists and is a driver.
- Every `item_ref` exists and **belongs to the order's restaurant**.

### 7.4 Order rules
- At least 1 item.
- At most 12 items in total quantity.
- Order total (sum of `quantity × unit_price`) is 1.00 to 1000.00.
- Timeline: `placed_at ≤ accepted_at ≤ picked_up_at ≤ delivered_at` (ignoring missing ones).
  This must match the database's `orders_timeline_check`, so a bad row never reaches the database.
- `delivered` → `delivered_at` is present.
- `cancelled` → `cancelled_at` is present and `delivered_at` is empty.
- A rejected order rejects all its items.

### 7.5 Duplicates
- Within one file, if a ref appears more than once, **the last row wins**; each earlier row is
  skipped with a WARNING.
- Within one order, the same `item_ref` twice: last one wins, WARNING. (Each item appears
  once per order, with its total quantity.)
- A ref already loaded on an earlier day: handled by `ON CONFLICT` (section 6).

## 8. Logging

- Use Python's `logging` module.
- Log files go in `logs/` at the project root (listed in `.gitignore`).
- One log file per run: `logs/ingest_YYYY-MM-DDTHH-MM-SS.log`. The same messages are also
  printed to the console.

### Format

```
<timestamp UTC> <LEVEL> <folder> <file>:<line> <ref> <message>
```

```
2026-10-20T03:30:01Z INFO    2026/10/19 -                    -               folder started
2026-10-20T03:30:01Z WARNING 2026/10/19 activity/orders.jsonl:14 O-20261019-0013 duplicate, replaced by line 22
2026-10-20T03:30:01Z ERROR   2026/10/19 activity/orders.jsonl:31 O-20261019-0030 rejected: delivered_at before picked_up_at
2026-10-20T03:30:02Z INFO    2026/10/19 -                    -               loaded: 3 customers, 34 orders, 88 items; rejected: 1 order
```

- `<line>` is the line number in the file (CSV header is line 1).
- Use `-` when a part doesn't apply.

### Levels
| Level | Used for |
|---|---|
| INFO | folder started, folder skipped (no `_DONE` / already loaded), per-folder summary |
| WARNING | duplicate replaced (data kept, but something odd happened) |
| ERROR | rejected row or file (with the reason), folder rolled back, changed checksum |

### End of run
Print one summary line per folder and a final total.

## 9. Database changes this needs

- `external_ref text UNIQUE` on `restaurants`, `menu_items`, `users`, `orders`.
- `active boolean NOT NULL DEFAULT true` on `menu_items` and `users`.
- `city` on `contacts` (customers and drivers have a city).
- `created_at timestamptz` on `users` (customer `signed_up_at`).
- The `file_loads` table.

## 10. Acceptance tests

1. Load all folders, record the row counts.
2. Run again: counts unchanged, every folder logged as "already loaded".
3. Add a deliberate crash after the 10th order, run on a fresh database: that folder has
   **zero** rows loaded. Remove the crash, run again: everything loads.
4. (With `--messy`, later) every injected bad record appears in the log with the right reason,
   and no valid record is rejected.

## 11. Open decisions

- **Old logs.** Original idea: delete the old log file on every run. This spec keeps one
  file per run instead, so runs can be compared. Choose one.
- **Inactive items and drivers.** This spec rejects orders that use an inactive menu item or
  restaurant. Should an inactive *driver* also cause a rejection?
- **`unit_price` vs menu price.** This spec only checks the 0.10–100.00 range. Should it also
  reject (or warn) when `unit_price` differs from the menu price?
- **Status updates across days.** Orders already loaded are never updated
  (`DO NOTHING`). Switch to `DO UPDATE` if the partner should be able to send later status changes.
