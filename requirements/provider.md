# Provider requirements

The provider is a script that **pretends to be an outside partner** sending us data files.
It writes the files; it never touches the database. The ingester (see `ingester.md`) loads them.

- Partner name: `redmondtownservice`
- Code: `provider/` (separate from `src/`; the two never import each other)
- Run from the project root: `python -m provider.generator --start 2026-09-01 --days 30`

## 1. Output location and folder layout

```
data/incoming/
  redmondtownservice/
    2026/10/19/
      reference/            # rarely changes; only present when something changed
        restaurants.csv
        menu_items.csv
        drivers.csv
      activity/             # every day
        customers.csv
        orders.jsonl
      _DONE                 # empty file, written LAST
```

- One folder per day: `YYYY/MM/DD`.
- **Day one** (`--start` date): `reference/` contains every restaurant, menu item and driver.
- **Later days**: a reference file is written only if something in it changed, and it contains
  only the changed rows.
- `activity/` is written every day.
- `_DONE` is written after all other files are complete. It tells the ingester the delivery is finished.
- The provider refuses to overwrite a day folder that already exists, unless `--overwrite` is given.
- `data/incoming/` is generated, so it is listed in `.gitignore`.

## 2. File formats

### CSV files (`restaurants.csv`, `menu_items.csv`, `drivers.csv`, `customers.csv`)
- Comma-separated, first line is the header, UTF-8.
- Values containing a comma are wrapped in double quotes (standard CSV quoting).
- One record per line.

### JSON Lines file (`orders.jsonl`)
- One order per line, each line a complete JSON object. No blank lines.
- Each order contains its items in an `items` list.
- UTF-8.

### Common value formats
| Kind | Format | Example |
|---|---|---|
| Timestamp | UTC, `YYYY-MM-DDTHH:MM:SS.sssZ` (always 3 decimal digits) | `2026-10-19T19:05:00.000Z` |
| Date | `YYYY-MM-DD` | `2024-03-15` |
| Money | dollars, 2 decimal places | `9.50` |
| Phone | exactly 10 digits, no spaces or dashes | `4255550101` |
| Boolean | `true` / `false` | `true` |

### Partner IDs (refs)
| Thing | Pattern | Example |
|---|---|---|
| Restaurant | `R` + 3 digits | `R007` |
| Menu item | `M` + 4 digits | `M0071` |
| Driver | `D` + 3 digits | `D003` |
| Customer | `C` + 4 digits | `C0042` |
| Order | `O-` + `YYYYMMDD` + `-` + 4 digits | `O-20261019-0013` |

Refs never change and are never reused.

## 3. File contents

### reference/restaurants.csv
| Column | Required | Notes |
|---|---|---|
| restaurant_ref | yes | |
| name | yes | |
| cuisine | yes | one of: American, Chinese, Indian, Italian, Japanese, Mediterranean, Mexican, Thai |
| city | yes | |
| opened_at | yes | date |
| owner_name | yes | the restaurant's owner becomes a user account |
| owner_email | yes | |
| owner_phone | yes | |
| active | yes | `false` = restaurant closed |

### reference/menu_items.csv
| Column | Required | Notes |
|---|---|---|
| item_ref | yes | |
| restaurant_ref | yes | must be a restaurant from this or an earlier delivery |
| name | yes | |
| price | yes | 0.10 to 100.00 |
| active | yes | `false` = removed from the menu |

### reference/drivers.csv
| Column | Required |
|---|---|
| driver_ref | yes |
| name | yes |
| email | yes |
| phone | yes |
| city | yes |
| active | yes (`false` = driver left) |

### activity/customers.csv
New customers who signed up that day.

| Column | Required |
|---|---|
| customer_ref | yes |
| name | yes |
| email | yes |
| phone | yes |
| address | yes |
| city | yes |
| signed_up_at | yes (timestamp) |

### activity/orders.jsonl
One order per line:

```json
{"order_ref": "O-20261019-0013", "customer_ref": "C0042", "restaurant_ref": "R007", "driver_ref": "D003", "status": "delivered", "placed_at": "2026-10-19T19:05:00.000Z", "accepted_at": "2026-10-19T19:07:00.000Z", "picked_up_at": "2026-10-19T19:25:00.000Z", "delivered_at": "2026-10-19T19:41:00.000Z", "cancelled_at": null, "items": [{"item_ref": "M0071", "quantity": 2, "unit_price": 9.50}, {"item_ref": "M0074", "quantity": 1, "unit_price": 3.00}]}
```

| Field | Required | Notes |
|---|---|---|
| order_ref | yes | |
| customer_ref | yes | |
| restaurant_ref | yes | |
| driver_ref | no | `null` if no driver was assigned (e.g. cancelled early) |
| status | yes | `placed`, `accepted`, `preparing`, `picked_up`, `delivered`, `cancelled` |
| placed_at | yes | |
| accepted_at | no | `null` if it hasn't happened |
| picked_up_at | no | |
| delivered_at | no | |
| cancelled_at | no | |
| items | yes | list with at least 1 item |
| items[].item_ref | yes | must belong to the order's restaurant |
| items[].quantity | yes | whole number, at least 1 |
| items[].unit_price | yes | price at the time of the order |

## 4. Changes to reference data

Every reference row carries an `active` column:

| The ref is… | Meaning |
|---|---|
| new | add it |
| already known | update it (e.g. new price or name) |
| known, `active = false` | switch it off; never delete |

## 5. Data the provider must respect (valid data)

- Menu item price: 0.10 to 100.00.
- An order has 1 or more items, and **at most 12 items in total quantity** (2 tacos + 1 drink = 3).
- Order total (sum of `quantity × unit_price`): 1.00 to 1000.00.
- `unit_price` equals the menu item's price on the day of the order.
- Timeline: `placed_at ≤ accepted_at ≤ picked_up_at ≤ delivered_at`.
- `delivered` orders have `delivered_at`. `cancelled` orders have `cancelled_at` and no `delivered_at`.
- Every ref in a file points to something delivered on the same day or earlier.
- Items in an order come from that order's restaurant, and are active.

## 6. Volume (default run)

| Data | Amount |
|---|---|
| Days | 30 |
| Restaurants | 16 (2 per cuisine) |
| Menu items | 10–15 per restaurant (~200) |
| Drivers | 15 |
| Customers | 100 on day one, plus 0–5 new per day |
| Orders | ~1,000 in total (25–45 per day) |
| Items per order | 1–4 lines |

All amounts are settings, so larger runs are possible later.

## 7. Realistic patterns

So the charts have something to find:
- More orders at lunch (11:00–13:00) and dinner (18:00–21:00) **Pacific time**, converted to UTC in the files.
- More orders on Friday and Saturday.
- Some cuisines are more popular than others (fixed weights).
- Each restaurant has its own typical prep speed; some are consistently slow.
- Prep and delivery durations use NumPy random distributions (e.g. normal), never negative.
- 3–5% of orders are cancelled, more often at slow restaurants.
- A few menu price changes and one or two driver changes during the 30 days, to exercise reference updates.

## 8. Reproducibility

- Default seed = year and month of `--start` (`2026-09-01` → `202609`). Each month gets its own
  dataset, and re-running the same command produces exactly the same files.
- `--seed N` overrides the default (e.g. to get a different dataset for the same month).
- Generate a whole period in **one run** (e.g. `--start 2026-09-01 --days 61` for Sept + Oct).
  Every run starts a fresh world (refs `R001`, `C0001`... again), so two separate runs must not be
  loaded into the same database.

## 9. Later: messy data (phase 2)

Behind a flag (`--messy`), the provider will inject a small number of bad records so the
ingester's validation can be tested, for example:
- missing required field, bad email, 9-digit phone
- unknown restaurant/customer/item ref
- item from a different restaurant
- timestamps out of order, status that contradicts timestamps
- quantity 0, price out of range, more than 12 items
- duplicate order in the same file
- a broken JSON line, a CSV row with the wrong number of columns

Not part of the first version.
