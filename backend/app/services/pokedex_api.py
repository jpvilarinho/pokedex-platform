import asyncio
import random
import httpx
from app.core.config import settings

_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)


def _normalize_detail(payload: dict) -> dict:
    return {
        "id": payload["id"],
        "name": payload["name"],
        "sprite": (payload.get("sprites") or {}).get("front_default"),
        "height": payload.get("height"),
        "weight": payload.get("weight"),
        "types": [t["type"]["name"] for t in payload.get("types", [])],
        "abilities": [a["ability"]["name"] for a in payload.get("abilities", [])],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in payload.get("stats", [])},
        "moves": [m["move"]["name"] for m in payload.get("moves", [])][:200],
    }


async def _request_with_retry(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict | None = None,
    max_attempts: int = 4,
) -> httpx.Response:
    """
    Retry simples com backoff exponencial + jitter.
    - Re-tenta para 429 e 5xx.
    - Propaga o erro em 4xx (exceto 429).
    """
    base_sleep = 0.25
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            r = await client.get(url, params=params)
            # 429 e 5xx -> retry
            if r.status_code == 429 or 500 <= r.status_code <= 599:
                if attempt == max_attempts:
                    r.raise_for_status()
                sleep_for = base_sleep * (2 ** (attempt - 1)) + random.random() * 0.15
                await asyncio.sleep(sleep_for)
                continue

            # outros 4xx -> falha direta
            r.raise_for_status()
            return r

        except Exception as e:
            last_exc = e
            if attempt == max_attempts:
                raise
            sleep_for = base_sleep * (2 ** (attempt - 1)) + random.random() * 0.15
            await asyncio.sleep(sleep_for)

    # não deveria chegar aqui
    if last_exc:
        raise last_exc
    raise RuntimeError("Unexpected retry state")


async def fetch_pokemon_list(client: httpx.AsyncClient, offset: int = 0, limit: int = 100000) -> list[dict]:
    r = await _request_with_retry(
        client,
        f"{settings.POKEAPI_BASE}/pokemon",
        params={"offset": offset, "limit": limit},
    )
    return r.json()["results"]


async def fetch_pokemon_detail_by_url(client: httpx.AsyncClient, url: str) -> dict:
    async with _semaphore:
        r = await _request_with_retry(client, url)
        return _normalize_detail(r.json())


async def fetch_pokemon_detail_by_id(client: httpx.AsyncClient, pokemon_id: int) -> dict:
    async with _semaphore:
        r = await _request_with_retry(client, f"{settings.POKEAPI_BASE}/pokemon/{pokemon_id}")
        return _normalize_detail(r.json())


async def fetch_pokemon_species_by_id(client: httpx.AsyncClient, pokemon_id: int) -> dict:
    async with _semaphore:
        r = await _request_with_retry(client, f"{settings.POKEAPI_BASE}/pokemon-species/{pokemon_id}")
        return r.json()


async def fetch_evolution_chain_by_url(client: httpx.AsyncClient, url: str) -> dict:
    async with _semaphore:
        r = await _request_with_retry(client, url)
        return r.json()


async def fetch_type_by_name(client: httpx.AsyncClient, type_name: str) -> dict:
    async with _semaphore:
        r = await _request_with_retry(client, f"{settings.POKEAPI_BASE}/type/{type_name}")
        return r.json()


def make_client(*, transport: httpx.AsyncBaseTransport | None = None) -> httpx.AsyncClient:
    """
    transport opcional facilita mock em testes (MockTransport).
    """
    return httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS, transport=transport)