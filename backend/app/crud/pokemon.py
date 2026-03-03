from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pokemon import Pokemon

async def upsert_pokemon(session: AsyncSession, data: dict) -> Pokemon:
    existing = await session.get(Pokemon, data["id"])
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        await session.commit()
        await session.refresh(existing)
        return existing

    obj = Pokemon(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

async def get_pokemon(session: AsyncSession, pokemon_id: int) -> Pokemon | None:
    return await session.get(Pokemon, pokemon_id)

async def list_pokemon_sorted(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
    name: str | None = None,
    captured_only: bool = False,
):
    stmt = select(Pokemon).order_by(Pokemon.name.asc()).offset(offset)

    if name:
        stmt = stmt.where(Pokemon.name.ilike(f"%{name}%"))

    if captured_only:
        stmt = stmt.where(Pokemon.captured.is_(True))

    if limit is not None:
        stmt = stmt.limit(limit)

    return (await session.execute(stmt)).scalars().all()

async def count_pokemon(
    session: AsyncSession,
    name: str | None = None,
    captured_only: bool = False,
) -> int:
    stmt = select(func.count()).select_from(Pokemon)

    if name:
        stmt = stmt.where(Pokemon.name.ilike(f"%{name}%"))

    if captured_only:
        stmt = stmt.where(Pokemon.captured.is_(True))

    return (await session.execute(stmt)).scalar_one()

async def set_pokemon_captured(
    session: AsyncSession,
    pokemon_id: int,
    captured: bool,
) -> Pokemon:
    p = await session.get(Pokemon, pokemon_id)
    if not p:
        raise ValueError("Pokemon not found")

    p.captured = captured
    await session.commit()
    await session.refresh(p)
    return p