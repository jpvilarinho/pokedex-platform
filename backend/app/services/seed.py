from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pokemon import Pokemon

SEED = [
    {
        "id": 25,
        "name": "pikachu",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
        "height": 4,
        "weight": 60,
        "types": ["electric"],
        "abilities": ["static", "lightning-rod"],
        "stats": {"hp": 35, "attack": 55, "defense": 40, "special_attack": 50, "special_defense": 50, "speed": 90},
        "moves": ["thunder-shock", "quick-attack"],
    },
    {
        "id": 1,
        "name": "bulbasaur",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        "height": 7,
        "weight": 69,
        "types": ["grass", "poison"],
        "abilities": ["overgrow", "chlorophyll"],
        "stats": {"hp": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65, "speed": 45},
        "moves": ["tackle", "vine-whip"],
    },
    {
        "id": 4,
        "name": "charmander",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
        "height": 6,
        "weight": 85,
        "types": ["fire"],
        "abilities": ["blaze", "solar-power"],
        "stats": {"hp": 39, "attack": 52, "defense": 43, "special_attack": 60, "special_defense": 50, "speed": 65},
        "moves": ["scratch", "ember"],
    },
]

async def seed_pokemons(db: AsyncSession, count: int = 3) -> int:
    created = 0
    for data in SEED[:count]:
        exists = await db.scalar(select(Pokemon).where(Pokemon.id == data["id"]))
        if exists:
            continue
        db.add(Pokemon(**data))
        created += 1

    if created:
        await db.commit()
    return created