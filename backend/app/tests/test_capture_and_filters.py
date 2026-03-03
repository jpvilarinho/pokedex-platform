import httpx
import pytest
from app.main import app
from app.tests.conftest import insert_pokemon


@pytest.mark.asyncio
async def test_captured_only_filter(db_session):
    await insert_pokemon(
        db_session,
        id=1,
        name="aaa",
        sprite=None,
        height=None,
        weight=None,
        types=[],
        abilities=[],
        stats={},
        moves=[],
        description=None,
        genus=None,
        egg_groups=[],
        gender_rate=None,
        evolution_chain=[],
        weaknesses=[],
        captured=True,
    )
    await insert_pokemon(
        db_session,
        id=2,
        name="bbb",
        sprite=None,
        height=None,
        weight=None,
        types=[],
        abilities=[],
        stats={},
        moves=[],
        description=None,
        genus=None,
        egg_groups=[],
        gender_rate=None,
        evolution_chain=[],
        weaknesses=[],
        captured=False,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/pokemon", params={"captured_only": "true"})
        assert r.status_code == 200
        payload = r.json()
        assert payload["total"] == 1
        assert len(payload["items"]) == 1
        assert payload["items"][0]["id"] == 1
        assert payload["items"][0]["captured"] is True


@pytest.mark.asyncio
async def test_capture_and_release(db_session):
    await insert_pokemon(
        db_session,
        id=10,
        name="capturable",
        sprite=None,
        height=None,
        weight=None,
        types=[],
        abilities=[],
        stats={},
        moves=[],
        description=None,
        genus=None,
        egg_groups=[],
        gender_rate=None,
        evolution_chain=[],
        weaknesses=[],
        captured=False,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.post("/pokemon/10/capture")
        assert r1.status_code == 200
        assert r1.json() == {"id": 10, "captured": True}

        r2 = await ac.delete("/pokemon/10/capture")
        assert r2.status_code == 200
        assert r2.json() == {"id": 10, "captured": False}


@pytest.mark.asyncio
async def test_capture_404_when_not_found():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/pokemon/999999/capture")
        assert r.status_code == 404