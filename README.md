# Dishpatch

A food delivery backend (think DoorDash), built as a learning project with **FastAPI**,
**SQLAlchemy**, **PostgreSQL**, **pgAdmin** and **Docker Compose**.

Restaurants come in two ways:
- a pretend **delivery partner** drops daily data files (restaurants, menus, drivers, customers,
  orders), and an **ingester** loads them into Postgres;
- the **API** lets you onboard restaurants, sign up customers and place orders.

## How the pieces fit

```
provider/  --writes daily files-->  data/incoming/  --ingester-->  Postgres  <--API--  Insomnia / /docs
(pretend partner)                   (CSV + JSONL)    (src/ingester)  (db)     (src/app)
```

| Service | URL | What it is |
|---|---|---|
| api | http://localhost:8000/docs | FastAPI, with interactive docs |
| db | localhost:5434 | PostgreSQL 16 (database `dishpatch`) |
| pgadmin | http://localhost:5050 | browse the database (no login needed) |

## Running it

**1. Create a `.env` file** in the project folder (it is git-ignored, never committed):
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<pick a password>
```

**2. Start everything:**
```bash
docker compose up --build
```
On the first start, Postgres runs `src/data/sql/dishpatch.sql`, which creates the 12 tables
and the 8 cuisines. Check it worked: http://localhost:8000/health

**3. Generate partner data** (runs on your machine, in a virtual environment):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r provider/requirements.txt
python -m provider.generator --start 2026-09-01 --days 30
```
This writes 30 days of files to `data/incoming/redmondtownservice/YYYY/MM/DD/`.
The same start date always produces the same data (the random seed comes from the date).

**4. Load the data into Postgres:**
```bash
docker compose exec api python -m src.ingester --in data/incoming/redmondtownservice
```
Running it again is safe: files already loaded are skipped (they are logged in `file_loads`),
and rows are matched by their partner id (`external_ref`), so nothing is duplicated.
Result: 16 restaurants, 199 menu items, 16 drivers, 174 customers, 1167 orders.

**5. Try the API** at http://localhost:8000/docs, or with Insomnia / Postman using
`base_url = http://localhost:8000`.

pgAdmin already knows the server (from `pgadmin/servers.json`); it asks only for the
database password from `.env`.

## API

Full requirements and decisions: [`requirements/api.md`](requirements/api.md).

### Restaurants
| Method | Path | Does |
|---|---|---|
| GET | `/restaurants` | all operational restaurants, with cuisine and active dishes |
| GET | `/restaurants/{id}` | one restaurant |
| POST | `/restaurants` | onboard a restaurant: owner account, restaurant and menu in one request |
| PATCH | `/restaurants/{id}` | change only the fields sent; add dishes (`add_menu_items`) and remove dishes (`remove_menu_item_ids`) |
| DELETE | `/restaurants/{id}` | soft delete: `operational = false` |
| PATCH | `/restaurants/{id}/reactivate` | switch a deleted restaurant back on |

### Customers
| Method | Path | Does |
|---|---|---|
| POST | `/customers` | sign up a customer |
| GET | `/customers/{id}` | one customer (404 if the user is not a customer) |

### Orders
| Method | Path | Does |
|---|---|---|
| POST | `/orders` | place an order |
| GET | `/orders/{id}` | one order with its items and total |

Example: place an order
```json
POST /orders
{
  "customer_id": 175,
  "restaurant_id": 18,
  "items": [
    { "menu_item_id": 200, "quantity": 2 },
    { "menu_item_id": 202, "quantity": 1 }
  ]
}
```
The request has **no prices**: each line's `unit_price` is copied from the dish's current price
in the database, so a client cannot set its own price, and old orders keep the price they were
placed at.

### Rules and status codes
| Code | When |
|---|---|
| 201 | created (restaurant, customer, order) |
| 400 | unknown cuisine, closed restaurant, dish not on this restaurant's menu or inactive, the same dish twice, more than 12 items |
| 404 | the restaurant, customer or order doesn't exist |
| 409 | email or restaurant name already registered |
| 422 | the request doesn't match the schema (checked automatically by Pydantic) |
| 503 | the database is down |

## Design notes

- **Soft deletes.** Restaurants and dishes are switched off (`operational`, `active`), never
  removed, because past orders still point to them.
- **One transaction per request.** A create or update saves everything or nothing: an error
  halfway through (for example a bad dish id in a PATCH) leaves the database unchanged.
- **No N+1 queries.** The restaurant list loads all menus and cuisines with `selectinload`:
  2 extra queries in total instead of one per restaurant.
- **People are spread over 4 tables:** `users -> accounts -> profiles -> contacts`. An account's
  `type` (`Customer`, `Restaurant`, `Driver`) says who the user is.
- **Orders and dishes are many-to-many** through `order_items`, which also stores the quantity
  and the price at the time of the order.

The diagram of all tables is [`docs/dishpatch_erd.drawio`](docs/dishpatch_erd.drawio)
(open it with draw.io or the VS Code Draw.io extension).

## Project layout

```
docker-compose.yml        db, pgadmin and api services
Dockerfile                builds the api image
requirements.txt          API dependencies
requirements/             requirements and decisions: provider.md, ingester.md, api.md
docs/                     ER diagram
pgadmin/servers.json      registers the database in pgAdmin automatically

provider/                 the pretend partner: generates daily CSV / JSONL files
  generator.py              entry point (command-line options)
  reference.py, activity.py restaurants, menus, drivers / customers, orders
  models/                   dataclasses for the generated data

src/data/sql/dishpatch.sql  the database schema (runs on the first start)
src/ingester/             loads partner files into Postgres, one loader per file type
src/app/                  the API
  main.py                   creates the app, includes the routers
  database.py               engine, session, get_db()
  models/                   SQLAlchemy models: one class per table
  schemas.py                Pydantic schemas: the JSON the API accepts and returns
  routers/                  the endpoints: restaurants.py, customers.py, orders.py
```

## Resetting the database

The schema script only runs when the database volume is empty. To start over:
```bash
docker compose down -v      # deletes the database volume and all its data
docker compose up --build
```
Then run the ingester again (step 4).

## Not done yet

- Login: passwords are a default (`changeme`) and stored as-is; no hashing or JWT tokens yet,
  so anyone can place an order for any customer id.
- Changing a single dish's name or price (`PATCH /menu-items/{id}`).
- Order status updates (accepted, picked up, delivered) and assigning drivers.
- Menus (the `menus` table exists but isn't used yet).
- Database migrations (Alembic).
