import httpx
import pytest
from app.main import app
from app.tests.conftest import insert_pokemon


@pytest.mark.asyncio
async def test_pagination_offset_limit_and_sorted(db_session):
    await insert_pokemon(
        db_session, id=1, name="charmander", sprite=None, height=None, weight=None,
        types=[], abilities=[], stats={}, moves=[],
        description=None, genus=None, egg_groups=[], gender_rate=None, evolution_chain=[], weaknesses=[],
        captured=False,
    )
    await insert_pokemon(
        db_session, id=2, name="bulbasaur", sprite=None, height=None, weight=None,
        types=[], abilities=[], stats={}, moves=[],
        description=None, genus=None, egg_groups=[], gender_rate=None, evolution_chain=[], weaknesses=[],
        captured=False,
    )
    await insert_pokemon(
        db_session, id=3, name="pikachu", sprite=None, height=None, weight=None,
        types=[], abilities=[], stats={}, moves=[],
        description=None, genus=None, egg_groups=[], gender_rate=None, evolution_chain=[], weaknesses=[],
        captured=False,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r0 = await ac.get("/pokemon")
        assert r0.status_code == 200
        assert r0.json()["total"] == 3
        assert [x["name"] for x in r0.json()["items"]] == ["bulbasaur", "charmander", "pikachu"]

        r1 = await ac.get("/pokemon", params={"limit": 1, "offset": 0})
        assert r1.status_code == 200
        assert [x["name"] for x in r1.json()["items"]] == ["bulbasaur"]

        r2 = await ac.get("/pokemon", params={"limit": 1, "offset": 1})
        assert r2.status_code == 200
        assert [x["name"] for x in r2.json()["items"]] == ["charmander"]

        r3 = await ac.get("/pokemon", params={"limit": 1, "offset": 2})
        assert r3.status_code == 200
        assert [x["name"] for x in r3.json()["items"]] == ["pikachu"]