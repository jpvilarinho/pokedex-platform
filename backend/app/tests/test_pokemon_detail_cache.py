import httpx
import pytest
from app.main import app


@pytest.mark.asyncio
async def test_pokemon_detail_fetches_once_then_uses_db(patch_make_client):
    counters = patch_make_client

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.get("/pokemon/999")
        assert r1.status_code == 200
        assert r1.json()["id"] == 999
        assert counters.get("pokemon_999", 0) == 1

        r2 = await ac.get("/pokemon/999")
        assert r2.status_code == 200
        assert r2.json()["name"] == "testmon"
        assert counters.get("pokemon_999", 0) == 1