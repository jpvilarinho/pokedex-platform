import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_pokemon_list_empty_db_returns_200():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/pokemon")
        assert r.status_code == 200
        payload = r.json()
        assert payload["total"] == 0
        assert payload["items"] == []