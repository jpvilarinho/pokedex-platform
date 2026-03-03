import httpx
import pytest
from app.main import app
from app.tests.conftest import insert_pokemon


@pytest.mark.asyncio
async def test_export_xml_headers_and_content(db_session):
    await insert_pokemon(
        db_session,
        id=1,
        name="bulbasaur",
        sprite="http://img/b.png",
        height=7,
        weight=69,
        types=["grass"],
        abilities=["overgrow"],
        stats={"hp": 45},
        moves=["tackle"],
        description="desc",
        genus="Seed Pokémon",
        egg_groups=["monster"],
        gender_rate=1,
        evolution_chain=["bulbasaur"],
        weaknesses=["fire"],
        captured=True,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/pokemon/export/xml")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/xml")
        assert "attachment" in r.headers.get("content-disposition", "").lower()

        body = r.text
        assert body.startswith("<?xml")
        assert "<pokedex" in body
        assert 'pokemon' in body
        assert 'name="bulbasaur"' in body
        assert "<captured>true</captured>" in body