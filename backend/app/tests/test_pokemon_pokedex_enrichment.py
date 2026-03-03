import httpx
import pytest
from app.main import app


@pytest.mark.asyncio
async def test_pokedex_detail_enriches_and_persists(patch_make_client):
    counters = patch_make_client

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/pokemon/999/pokedex")
        assert r.status_code == 200
        payload = r.json()

        assert payload["id"] == 999
        assert payload["description"] is not None
        assert payload["genus"] == "Test Pokémon"
        assert payload["egg_groups"] == ["field"]
        assert payload["gender_rate"] == 4
        assert payload["evolution_chain"] == ["testmon", "testmon2"]
        assert payload["weaknesses"] == ["ground"]

        assert counters.get("pokemon_999", 0) >= 1
        assert counters.get("species_999", 0) >= 1
        assert counters.get("evo_777", 0) >= 1
        assert counters.get("type_electric", 0) >= 1

        r2 = await ac.get("/pokemon/999/pokedex")
        assert r2.status_code == 200
        assert r2.json()["id"] == 999


@pytest.mark.asyncio
async def test_pokedex_detail_404_when_pokeapi_returns_404(patch_make_client):
    _ = patch_make_client

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/pokemon/404/pokedex")
        assert r.status_code == 404