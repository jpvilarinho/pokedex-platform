#!/usr/bin/env sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, asyncio, asyncpg

async def main():
    dsn = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    for i in range(60):
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            print("DB is ready!")
            return
        except Exception as e:
            print(f"DB not ready yet ({i+1}/60): {e}")
            await asyncio.sleep(1)
    raise SystemExit("DB did not become ready in time")

asyncio.run(main())
PY

echo "Running migrations..."
alembic upgrade head

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000