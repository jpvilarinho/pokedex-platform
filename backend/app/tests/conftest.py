from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator, Iterator
from typing import Any

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.core import db as db_module
from app.main import app
from app.models.pokemon import Pokemon

from app.services import pokedex_api as pokedex_api_module
from app.api.routes import pokemon as pokemon_routes_module


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture()
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture(autouse=True)
def override_get_db(db_session: AsyncSession) -> Iterator[None]:
    async def _get_db_override() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[db_module.get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def clear_db(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """
    IMPORTANTÍSSIMO:
    Como o engine SQLite in-memory é compartilhado pela sessão,
    deve-se limpar a tabela antes de cada teste pra evitar vazamento de estado.
    """
    await db_session.execute(delete(Pokemon))
    await db_session.commit()
    yield


async def insert_pokemon(db: AsyncSession, **kwargs: Any) -> Pokemon:
    p = Pokemon(**kwargs)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@pytest.fixture()
def pokeapi_mock_transport() -> tuple[httpx.MockTransport, dict[str, int]]:
    """
    Mock do PokeAPI (sem internet). Também expõe contadores por endpoint
    para validar cache/fetch.
    """
    counters: dict[str, int] = {}

    def bump(key: str) -> None:
        counters[key] = counters.get(key, 0) + 1

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path == "/api/v2/pokemon/999":
            bump("pokemon_999")
            return httpx.Response(
                200,
                json={
                    "id": 999,
                    "name": "testmon",
                    "sprites": {"front_default": "http://img/testmon.png"},
                    "height": 10,
                    "weight": 100,
                    "types": [{"type": {"name": "electric"}}],
                    "abilities": [{"ability": {"name": "static"}}],
                    "stats": [{"stat": {"name": "hp"}, "base_stat": 99}],
                    "moves": [{"move": {"name": "thunder-shock"}}],
                },
            )

        if path == "/api/v2/pokemon/404":
            bump("pokemon_404")
            return httpx.Response(404, json={"detail": "Not found"})

        if path == "/api/v2/pokemon-species/999":
            bump("species_999")
            return httpx.Response(
                200,
                json={
                    "egg_groups": [{"name": "field"}],
                    "gender_rate": 4,
                    "flavor_text_entries": [
                        {"language": {"name": "en"}, "flavor_text": "A test pokemon.\nNice."}
                    ],
                    "genera": [{"language": {"name": "en"}, "genus": "Test Pokémon"}],
                    "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/777/"},
                },
            )

        if path == "/api/v2/pokemon-species/404":
            bump("species_404")
            return httpx.Response(404, json={"detail": "Not found"})

        if path == "/api/v2/evolution-chain/777/":
            bump("evo_777")
            return httpx.Response(
                200,
                json={
                    "chain": {
                        "species": {"name": "testmon"},
                        "evolves_to": [{"species": {"name": "testmon2"}, "evolves_to": []}],
                    }
                },
            )

        if path == "/api/v2/type/electric":
            bump("type_electric")
            return httpx.Response(
                200,
                json={"damage_relations": {"double_damage_from": [{"name": "ground"}]}},
            )

        bump(f"unhandled:{path}")
        return httpx.Response(500, json={"error": f"Unhandled mock URL: {path}"})

    return httpx.MockTransport(handler), counters


@pytest.fixture()
def patch_make_client(pokeapi_mock_transport):
    """
    Patch do make_client em DOIS lugares:
    - app.services.pokedex_api.make_client (onde foi definido)
    - app.api.routes.pokemon.make_client (porque foi importado diretamente no router)

    Isso garante que os endpoints usem MockTransport e NUNCA a internet.
    """
    transport, counters = pokeapi_mock_transport

    def make_client_for_test(*, transport_override=None):
        t = transport_override or transport
        return httpx.AsyncClient(transport=t)

    original_services = pokedex_api_module.make_client
    original_routes = pokemon_routes_module.make_client

    pokedex_api_module.make_client = lambda *, transport=None: make_client_for_test(transport_override=transport)
    pokemon_routes_module.make_client = lambda *, transport=None: make_client_for_test(transport_override=transport)

    yield counters

    pokedex_api_module.make_client = original_services
    pokemon_routes_module.make_client = original_routes