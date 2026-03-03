"""add json defaults

Revision ID: 2066ed86c71a
Revises: f5e157227502
Create Date: 2026-02-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2066ed86c71a"
down_revision: Union[str, Sequence[str], None] = "f5e157227502"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Sonar: evitar duplicação de literais
JSON_EMPTY_ARRAY_DEFAULT = sa.text("'[]'::json")
JSON_EMPTY_OBJECT_DEFAULT = sa.text("'{}'::json")


def upgrade() -> None:
    # adiciona default no banco (bom para inserts fora do SQLAlchemy)
    op.alter_column(
        "pokemon",
        "types",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=JSON_EMPTY_ARRAY_DEFAULT,
    )
    op.alter_column(
        "pokemon",
        "abilities",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=JSON_EMPTY_ARRAY_DEFAULT,
    )
    op.alter_column(
        "pokemon",
        "moves",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=JSON_EMPTY_ARRAY_DEFAULT,
    )
    op.alter_column(
        "pokemon",
        "stats",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=JSON_EMPTY_OBJECT_DEFAULT,
    )


def downgrade() -> None:
    # remove o default do banco (volta ao estado anterior)
    op.alter_column(
        "pokemon",
        "types",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "pokemon",
        "abilities",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "pokemon",
        "moves",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "pokemon",
        "stats",
        existing_type=sa.JSON(),
        nullable=False,
        server_default=None,
    )