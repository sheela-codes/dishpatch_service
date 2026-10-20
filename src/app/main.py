import os

import psycopg
from fastapi import FastAPI, HTTPException

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Dishpatch API")


@app.get("/")
def root():
    return {"service": "dishpatch", "docs": "/docs"}


@app.get("/health")
def health():
    """Check that the API can reach the database."""
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError as exc:
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}")
    return {"status": "ok", "database": "connected"}


@app.get("/tables")
def list_tables():
    """List the tables in the dishpatch database, to confirm the schema loaded."""
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        ).fetchall()
    return {"tables": [name for (name,) in rows]}
