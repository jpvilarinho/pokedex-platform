from pydantic import BaseModel

class PokemonListItem(BaseModel):
    id: int
    name: str
    sprite: str | None = None
    captured: bool

class PokemonDetail(BaseModel):
    id: int
    name: str
    sprite: str | None = None
    height: int | None = None
    weight: int | None = None
    types: list[str]
    abilities: list[str]
    stats: dict[str, int]
    moves: list[str]
    captured: bool

class PokemonPokedexDetail(PokemonDetail):
    description: str | None = None
    genus: str | None = None
    egg_groups: list[str] = []
    gender_rate: int | None = None
    evolution_chain: list[str] = []
    weaknesses: list[str] = []

class PaginatedResponse(BaseModel):
    total: int
    offset: int
    limit: int | None = None
    items: list[PokemonListItem]