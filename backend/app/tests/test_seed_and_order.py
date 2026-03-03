import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_seed_and_sorted_list():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        seed = await ac.post("/admin/seed", params={"count": 3})
        assert seed.status_code == 200

        r = await ac.get("/pokemon")
        assert r.status_code == 200
        names = [p["name"] for p in r.json()["items"]]
        assert names == sorted(names)