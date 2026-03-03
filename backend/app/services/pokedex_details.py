import asyncio
import httpx

from app.services.pokedex_api import (
    fetch_pokemon_detail_by_id,
    fetch_pokemon_species_by_id,
    fetch_evolution_chain_by_url,
    fetch_type_by_name,
)

def _pick_english_flavor_text(species: dict) -> str | None:
    for entry in species.get("flavor_text_entries", []):
        if (entry.get("language") or {}).get("name") == "en":
            text = (entry.get("flavor_text") or "").replace("\n", " ").replace("\f", " ").strip()
            return text or None
    return None

def _pick_english_genus(species: dict) -> str | None:
    for g in species.get("genera", []):
        if (g.get("language") or {}).get("name") == "en":
            return (g.get("genus") or "").strip() or None
    return None

def _flatten_evo_chain(chain: dict) -> list[str]:
    names: list[str] = []

    def walk(node: dict):
        s = node.get("species") or {}
        name = s.get("name")
        if name:
            names.append(name)
        for nxt in node.get("evolves_to", []) or []:
            walk(nxt)

    walk(chain.get("chain") or {})
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out

def _compute_weaknesses_from_types(type_payloads: list[dict]) -> list[str]:
    weaknesses = []
    for tp in type_payloads:
        rel = tp.get("damage_relations") or {}
        for w in rel.get("double_damage_from", []) or []:
            name = w.get("name")
            if name:
                weaknesses.append(name)
    return sorted(set(weaknesses))

async def build_pokedex_payload(client: httpx.AsyncClient, pokemon_id: int) -> dict:
    base_task = fetch_pokemon_detail_by_id(client, pokemon_id)
    species_task = fetch_pokemon_species_by_id(client, pokemon_id)
    base, species = await asyncio.gather(base_task, species_task)

    description = _pick_english_flavor_text(species)
    genus = _pick_english_genus(species)
    egg_groups = [e["name"] for e in (species.get("egg_groups") or []) if e.get("name")]
    gender_rate = species.get("gender_rate")

    evo_chain = []
    evo_url = (species.get("evolution_chain") or {}).get("url")
    if evo_url:
        evo_payload = await fetch_evolution_chain_by_url(client, evo_url)
        evo_chain = _flatten_evo_chain(evo_payload)

    type_names = base.get("types") or []
    type_tasks = [fetch_type_by_name(client, t) for t in type_names]
    type_payloads = await asyncio.gather(*type_tasks) if type_tasks else []
    weaknesses = _compute_weaknesses_from_types(type_payloads)

    return {
        **base,
        "description": description,
        "genus": genus,
        "egg_groups": egg_groups,
        "gender_rate": gender_rate,
        "evolution_chain": evo_chain,
        "weaknesses": weaknesses,
    }