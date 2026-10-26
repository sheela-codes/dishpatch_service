import os

import psycopg
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from src.app.routers import restaurants, customers

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Dishpatch API")
app.include_router(restaurants.router)
app.include_router(customers.router)
logging.basicConfig(level=logging.INFO)

@app.exception_handler(OperationalError)
def database_unavailable(request: Request, exc: OperationalError):
    return JSONResponse(status_code=503, content={"detail": "Database unavailable, please try again later"})


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
