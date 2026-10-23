"""Database connection for the ingester."""
import os

import psycopg


def connect() -> psycopg.Connection:
    """Connect using DATABASE_URL (set for the api container in docker-compose.yml).

    autocommit is off: nothing is saved until a transaction commits, so a failed
    folder leaves no partial rows behind.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set. Run the ingester inside the api container:\n"
                         "  docker compose exec api python -m src.ingester --in data/incoming/redmondtownservice")
    return psycopg.connect(url)
