from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.services.seed import seed_pokemons

router = APIRouter(prefix="/admin", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CountQuery = Annotated[int, Query(ge=1, le=50)]

@router.post("/seed")
async def seed(
    db: DbSession,
    count: CountQuery = 3,
):
    created = await seed_pokemons(db, count=count)
    return {"created": created}