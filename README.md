# Dishpatch

A food delivery service backend, built as a learning project with FastAPI, PostgreSQL, pgAdmin and Docker.

## Running it

1. Copy `.env.example` to `.env` and set a password.
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. Open:
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - pgAdmin: http://localhost:5050 (admin@example.com / admin123)

## Connecting pgAdmin to the database

Register a server with:
- Host: `db` (the compose service name, not `localhost`)
- Port: `5432`
- Username / password: the values from `.env`

## Project layout

```
docker-compose.yml     # db, pgadmin and api services
Dockerfile             # builds the api image
requirements.txt       # Python dependencies
src/app/main.py        # FastAPI app
src/data/sql/          # schema scripts, run on the database's first start
```

## Resetting the database

Schema scripts only run when the database volume is empty. After changing them:
```bash
docker compose down -v   # deletes the database volume and all its data
docker compose up --build
```
