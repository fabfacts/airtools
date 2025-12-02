"""fix timestamp unique constraint

Revision ID: a1b2c3d4e5f6
Revises: 74487000f258
Create Date: 2025-12-02 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "74487000f258"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint from timestamp, add composite unique on (sensor_id, timestamp)."""
    # SQLite requires batch mode for schema changes
    with op.batch_alter_table("sensordata", schema=None) as batch_op:
        # Drop the existing unique constraint on timestamp
        # SQLite autonames this constraint, so we drop all UNIQUE constraints
        # and recreate only the one we want
        batch_op.drop_constraint(None, type_="unique")

        # Create composite unique constraint
        batch_op.create_unique_constraint(
            "uq_sensordata_sensor_timestamp", ["sensor_id", "timestamp"]
        )


def downgrade() -> None:
    """Restore original timestamp unique constraint."""
    with op.batch_alter_table("sensordata", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_sensordata_sensor_timestamp", type_="unique"
        )
        batch_op.create_index(
            "ix_sensordata_timestamp", ["timestamp"], unique=True
        )
