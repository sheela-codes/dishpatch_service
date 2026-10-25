# API requirements

The Dishpatch API: onboard restaurants with their menus, sign up customers, and let customers
place orders. Built with FastAPI and SQLAlchemy on the existing Postgres schema
(`src/data/sql/dishpatch.sql`).

- Code: `src/app/`
- Docs while running: http://localhost:8000/docs
- Built in layers: each layer works on its own before the next one starts.

## 1. Stack and conventions

- **FastAPI** for the endpoints, **Pydantic** for request and response shapes,
  **SQLAlchemy 2.0** (ORM) for the database, with **psycopg 3** as its driver.
- The connection URL must start with `postgresql+psycopg://` (the `DATABASE_URL` from
  docker-compose starts with `postgresql://`, so `database.py` swaps the prefix).
- The tables already exist (created by `dishpatch.sql`). The API maps models onto them and never
  creates tables itself. Migrations (Alembic) are out of scope for now.
- Code stays compatible with **Python 3.9** (the course version): `Optional[str]`, not `str | None`.
- Records created through the API have no `external_ref` (that marks partner data from the ingester).
- Every create runs in **one transaction**: all of it is saved, or none of it.

## 2. Files

```
src/app/
  main.py            # creates the FastAPI app, includes the routers
  database.py        # engine, SessionLocal, Base, get_db()
  models.py          # SQLAlchemy models mapped onto the existing tables
  schemas.py         # Pydantic: what clients send and what the API returns
  routers/
    restaurants.py
    menu_items.py
    customers.py
    orders.py
```

## 3. Models

Mapped onto existing tables: `Contact`, `Profile`, `Account`, `User`, `Cuisine`, `Restaurant`,
`MenuItem`, `Order`, `OrderItem`.

- Relationships used in responses: `Restaurant.menu_items`, `Order.items`.
- The Postgres enum types `account_type` and `order_status` already exist; the models must use
  them, not try to create them.
- A person (owner or customer) is created as `contacts -> profiles -> accounts -> users`,
  the same chain the ingester uses.

## 4. Endpoints

### Layer 1: onboard and read restaurants

| Method | Path | Does |
|---|---|---|
| POST | `/restaurants` | onboard a restaurant: owner + restaurant + menu, in one request |
| GET | `/restaurants` | list restaurants |
| GET | `/restaurants/{id}` | one restaurant with its menu |

**POST /restaurants** request:
```json
{
  "name": "Pho Saigon",
  "cuisine": "Thai",
  "city": "Seattle",
  "opened_at": "2026-10-01",
  "owner": { "name": "Linh Tran", "email": "linh@example.com", "phone": "2065550199" },
  "menu_items": [
    { "name": "Pho Bo", "price": 15.50 },
    { "name": "Spring Rolls", "price": 7.00 }
  ]
}
```
Steps, in one transaction:
1. Look up the cuisine id by name (unknown cuisine: 400).
2. Create the owner: contact -> profile -> account (type `Restaurant`, default password) -> user.
3. Create the restaurant (`operational = true`).
4. Create each menu item for it.
5. Return **201** with the restaurant, its owner's user id, and its menu items with their new ids.

### Layer 2: update and delete (completes CRUD)

| Method | Path | Does |
|---|---|---|
| PATCH | `/restaurants/{id}` | change name, cuisine, city or opened_at (only the fields sent) |
| DELETE | `/restaurants/{id}` | **soft delete**: sets `operational = false` |
| POST | `/restaurants/{id}/menu-items` | add a dish to a restaurant's menu |
| PATCH | `/menu-items/{id}` | change a dish's name or price |
| DELETE | `/menu-items/{id}` | **soft delete**: sets `active = false` |

Old orders keep their prices after a price change, because `order_items` stores `unit_price`.

### Layer 3: customers and orders

| Method | Path | Does |
|---|---|---|
| POST | `/customers` | sign up a customer |
| GET | `/customers/{id}` | one customer |
| POST | `/orders` | place an order |
| GET | `/orders/{id}` | one order with its items and total |

**POST /customers** request:
```json
{ "name": "Maya Lee", "email": "maya@example.com", "phone": "4255550101",
  "address": "1234 Pine St, Apt 5", "city": "Seattle" }
```
Creates contact -> profile -> account (type `Customer`, default password) -> user.
Returns **201** with the new customer's id.

**POST /orders** request:
```json
{
  "customer_id": 175,
  "restaurant_id": 17,
  "items": [
    { "menu_item_id": 200, "quantity": 2 },
    { "menu_item_id": 201, "quantity": 1 }
  ]
}
```
Checks, then one transaction:
1. The customer exists and is a customer.
2. The restaurant exists and is operational.
3. Every dish exists, belongs to **this** restaurant, and is active.
4. Each quantity is at least 1; the total quantity is at most 12; no dish appears twice.
5. **`unit_price` is taken from the database (the dish's current price), never from the client.**
6. Insert the order (`status = 'placed'`, `placed_at = now`, no driver), then its `order_items`.
7. Return **201** with the order, its items and the total.

### Layer 4: nice to have

| Method | Path | Does |
|---|---|---|
| GET | `/customers/{id}/orders` | a customer's orders |
| PATCH | `/orders/{id}/status` | move an order along: `accepted`, `picked_up`, `delivered`, `cancelled`; sets the matching timestamp |

The database's `orders_timeline_check` constraint guarantees the timestamps stay in order.

## 5. Decisions

| Situation | Response |
|---|---|
| An owner's or customer's email already exists | **409 Conflict** |
| Delete a restaurant | **soft delete**: `operational = false` (orders still point at it) |
| Delete a menu item | **soft delete**: `active = false` |
| Password for new accounts | one constant default, `"changeme"`, stored as-is (hashing comes later) |
| The same dish twice in one order request | **400 Bad Request** |

## 6. Errors

| Code | When |
|---|---|
| 400 | invalid input the database can't accept: unknown cuisine, dish from another restaurant, inactive dish, closed restaurant, the same dish twice, more than 12 items |
| 404 | the id in the path (or in the body, e.g. `customer_id`) doesn't exist |
| 409 | the email is already registered |
| 422 | the request doesn't match the schema (FastAPI and Pydantic return this automatically) |

## 7. Out of scope for now

- Password hashing, login, JWT tokens.
- Alembic migrations (to be discussed once the models exist).
- Menus (`menu_items.menu_id` stays NULL; see `ingester.md`, open decisions).
- Assigning drivers to orders.

## 8. Open decisions

- **A restaurant name that's already taken** (`restaurants.name` is UNIQUE): suggested **409 Conflict**.
