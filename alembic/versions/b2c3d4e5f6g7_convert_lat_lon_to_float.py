"""convert lat lon to float

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-02 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert lat/lon columns from VARCHAR to REAL (float)."""
    # SQLite requires batch mode for type changes
    with op.batch_alter_table("sensor", schema=None) as batch_op:
        # Alter column types to Float
        batch_op.alter_column(
            "lon",
            existing_type=sa.String(),
            type_=sa.Float(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "lat",
            existing_type=sa.String(),
            type_=sa.Float(),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Revert lat/lon columns back to VARCHAR."""
    with op.batch_alter_table("sensor", schema=None) as batch_op:
        batch_op.alter_column(
            "lon",
            existing_type=sa.Float(),
            type_=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "lat",
            existing_type=sa.Float(),
            type_=sa.String(),
            existing_nullable=False,
        )
