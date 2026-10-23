"""Creating a person in the Dishpatch database.

A partner file describes a person in one row (name, email, phone, city).
The database spreads that over four tables, each pointing at the one before:

    contacts  <-  profiles  <-  accounts  <-  users

So creating a person is four inserts. Each one asks Postgres for the new row's id
(RETURNING id), so the next insert can point at it.
"""

IMPORTED_PASSWORD = "IMPORTED"   # not a real password hash, so it can never match a login


def users_by_email(conn) -> dict:
    """Everyone who already has an account: {email: users.id}. One query."""
    people = {}
    rows = conn.execute(
        "SELECT a.username, u.id FROM public.users u JOIN public.accounts a ON a.id = u.account_id"
    )
    for username, user_id in rows:
        people[username.lower()] = user_id
    return people


def insert_and_get_id(conn, sql: str, values: list) -> int:
    """Run an INSERT ... RETURNING id and give back the new id."""
    cursor = conn.execute(sql, values)
    new_row = cursor.fetchone()          # one row with one column: (42,)
    return new_row[0]                    # 42


def create_person(conn, name, email, phone, city, account_type, external_ref=None, created_at=None,
                  address=None) -> int:
    """Insert one person into the four tables. Returns the new users.id.

    account_type is 'Customer', 'Driver' or 'Restaurant'.
    external_ref is the partner's ref ('C0042', 'D003'); restaurant owners don't have one.
    address is only known for customers.
    """
    contact_id = insert_and_get_id(
        conn,
        "INSERT INTO public.contacts (phone_number, email, city, address) VALUES (%s, %s, %s, %s) RETURNING id",
        [phone, email, city, address],
    )
    profile_id = insert_and_get_id(
        conn,
        "INSERT INTO public.profiles (preferred_name, contact_id) VALUES (%s, %s) RETURNING id",
        [name, contact_id],
    )
    account_id = insert_and_get_id(
        conn,
        "INSERT INTO public.accounts (username, password, type, profile_id) VALUES (%s, %s, %s, %s) RETURNING id",
        [email, IMPORTED_PASSWORD, account_type, profile_id],
    )
    user_id = insert_and_get_id(
        conn,
        "INSERT INTO public.users (account_id, external_ref, created_at) VALUES (%s, %s, %s) RETURNING id",
        [account_id, external_ref, created_at],
    )
    return user_id
