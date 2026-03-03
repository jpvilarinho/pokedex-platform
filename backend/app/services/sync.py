import asyncio
from typing import Any, cast

import httpx

from app.services.pokedex_api import fetch_pokemon_list, fetch_pokemon_detail_by_url
from app.crud.pokemon import upsert_pokemon


async def sync_all_pokemon(session, client: httpx.AsyncClient, offset: int = 0, limit: int = 200) -> dict[str, Any]:
    raw_list = await fetch_pokemon_list(client, offset=offset, limit=limit)
    raw_list.sort(key=lambda x: x["name"])

    tasks = [fetch_pokemon_detail_by_url(client, item["url"]) for item in raw_list]

    results: list[dict] = []
    errors: list[str] = []

    for chunk_start in range(0, len(tasks), 200):
        chunk = tasks[chunk_start : chunk_start + 200]
        chunk_out = await asyncio.gather(*chunk, return_exceptions=True)

        for item in chunk_out:
            if isinstance(item, BaseException):
                errors.append(str(item))
                continue
            results.append(cast(dict, item))

    for p in results:
        await upsert_pokemon(session, p)

    return {"stored": len(results), "offset": offset, "limit": limit, "errors": errors[:20]}