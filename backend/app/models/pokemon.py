from sqlalchemy import String, Integer, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Pokemon(Base):
    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    sprite: Mapped[str | None] = mapped_column(String(300), nullable=True)

    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)

    types: Mapped[list] = mapped_column(JSON, default=list)
    abilities: Mapped[list] = mapped_column(JSON, default=list)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    moves: Mapped[list] = mapped_column(JSON, default=list)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genus: Mapped[str | None] = mapped_column(String(120), nullable=True)
    egg_groups: Mapped[list] = mapped_column(JSON, default=list)
    gender_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evolution_chain: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)

    captured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)