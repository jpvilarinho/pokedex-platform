from typing import Annotated, cast
import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.crud.pokemon import (
    count_pokemon,
    get_pokemon,
    list_pokemon_sorted,
    set_pokemon_captured,
    upsert_pokemon,
)
from app.models.pokemon import Pokemon
from app.schemas.pokemon import PaginatedResponse, PokemonDetail, PokemonListItem, PokemonPokedexDetail
from app.services.pokedex_api import fetch_pokemon_detail_by_id, make_client
from app.services.pokedex_details import build_pokedex_payload
from app.services.sync import sync_all_pokemon
from app.services.xml_export import pokemons_to_xml

router = APIRouter(prefix="/pokemon", tags=["pokemon"])
POKEMON_NOT_FOUND = "Pokemon not found"

_pokedex_locks: dict[int, asyncio.Lock] = {}

def _get_lock(pokemon_id: int) -> asyncio.Lock:
    lock = _pokedex_locks.get(pokemon_id)
    if lock is None:
        lock = asyncio.Lock()
        _pokedex_locks[pokemon_id] = lock
    return lock

DbSession = Annotated[AsyncSession, Depends(get_db)]

NameQuery = Annotated[str | None, Query(min_length=1)]
CapturedOnlyQuery = Annotated[bool, Query()]
OffsetQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int | None, Query(ge=1, le=settings.MAX_LIMIT)]

SyncOffsetQuery = Annotated[int, Query(ge=0)]
SyncLimitQuery = Annotated[int, Query(ge=1, le=500)]


@router.get("", response_model=PaginatedResponse)
async def get_pokemons(
    db: DbSession,
    name: NameQuery = None,
    captured_only: CapturedOnlyQuery = False,
    offset: OffsetQuery = 0,
    limit: LimitQuery = None,
):
    total = await count_pokemon(db, name=name, captured_only=captured_only)
    items_db = await list_pokemon_sorted(db, offset=offset, limit=limit, name=name, captured_only=captured_only)

    items = [PokemonListItem(id=p.id, name=p.name, sprite=p.sprite, captured=p.captured) for p in items_db]
    return PaginatedResponse(total=total, offset=offset, limit=limit, items=items)


@router.get("/export/xml")
async def export_xml(
    db: DbSession,
    name: NameQuery = None,
    captured_only: CapturedOnlyQuery = False,
):
    items = await list_pokemon_sorted(db, offset=0, limit=None, name=name, captured_only=captured_only)
    xml_bytes = pokemons_to_xml(items)

    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="pokedex.xml"'},
    )


@router.post("/sync")
async def sync(
    db: DbSession,
    offset: SyncOffsetQuery = 0,
    limit: SyncLimitQuery = 100,
):
    async with make_client() as client:
        result = await sync_all_pokemon(db, client, offset=offset, limit=limit)
    return result


@router.post(
    "/{pokemon_id}/capture",
    responses={404: {"description": "Pokemon not found"}},
)
async def capture_pokemon(pokemon_id: int, db: DbSession):
    p = await get_pokemon(db, pokemon_id)
    if not p:
        raise HTTPException(status_code=404, detail=POKEMON_NOT_FOUND)

    p = await set_pokemon_captured(db, pokemon_id, True)
    return {"id": p.id, "captured": p.captured}


@router.delete(
    "/{pokemon_id}/capture",
    responses={404: {"description": "Pokemon not found"}},
)
async def release_pokemon(pokemon_id: int, db: DbSession):
    p = await get_pokemon(db, pokemon_id)
    if not p:
        raise HTTPException(status_code=404, detail=POKEMON_NOT_FOUND)

    p = await set_pokemon_captured(db, pokemon_id, False)
    return {"id": p.id, "captured": p.captured}


@router.get(
    "/{pokemon_id}/pokedex",
    response_model=PokemonPokedexDetail,
    responses={404: {"description": "Pokemon not found"}},
)
async def get_pokemon_pokedex_detail(pokemon_id: int, db: DbSession):
    lock = _get_lock(pokemon_id)
    async with lock:
        p = await get_pokemon(db, pokemon_id)

        needs_enrichment = (
            (p is None)
            or (
                p.description is None
                and p.genus is None
                and not (p.weaknesses or [])
                and not (p.evolution_chain or [])
            )
        )

        if needs_enrichment:
            async with make_client() as client:
                try:
                    payload = await build_pokedex_payload(client, pokemon_id)
                except httpx.HTTPStatusError:
                    raise HTTPException(status_code=404, detail=POKEMON_NOT_FOUND)
            p = await upsert_pokemon(db, payload)

        if p is None:
            raise HTTPException(status_code=404, detail=POKEMON_NOT_FOUND)

        p = cast(Pokemon, p)

        return PokemonPokedexDetail(
            id=p.id,
            name=p.name,
            sprite=p.sprite,
            height=p.height,
            weight=p.weight,
            types=p.types or [],
            abilities=p.abilities or [],
            stats=p.stats or {},
            moves=p.moves or [],
            captured=p.captured,
            description=p.description,
            genus=p.genus,
            egg_groups=p.egg_groups or [],
            gender_rate=p.gender_rate,
            evolution_chain=p.evolution_chain or [],
            weaknesses=p.weaknesses or [],
        )


@router.get(
    "/{pokemon_id}",
    response_model=PokemonDetail,
    responses={404: {"description": "Pokemon not found"}},
)
async def get_pokemon_detail(pokemon_id: int, db: DbSession):
    p = await get_pokemon(db, pokemon_id)
    if not p:
        async with make_client() as client:
            try:
                data = await fetch_pokemon_detail_by_id(client, pokemon_id)
            except httpx.HTTPStatusError:
                raise HTTPException(status_code=404, detail=POKEMON_NOT_FOUND)
        p = await upsert_pokemon(db, data)

    return PokemonDetail(
        id=p.id,
        name=p.name,
        sprite=p.sprite,
        height=p.height,
        weight=p.weight,
        types=p.types or [],
        abilities=p.abilities or [],
        stats=p.stats or {},
        moves=p.moves or [],
        captured=p.captured,
    )
