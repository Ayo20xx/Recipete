"""Add admin roles and app-wide notifications.

Revision ID: c62be24a7f19
Revises: d24b8e63f091
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "c62be24a7f19"
down_revision: Union[str, Sequence[str], None] = "d24b8e63f091"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )

    with op.batch_alter_table("notification") as batch_op:
        batch_op.alter_column(
            "review_id",
            existing_type=sa.Uuid(),
            nullable=True,
        )
        batch_op.alter_column(
            "provider",
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=32),
            nullable=True,
        )
        batch_op.alter_column(
            "recipe_id",
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=64),
            nullable=True,
        )
        batch_op.add_column(
            sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("message", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True)
        )


def downgrade() -> None:
    op.execute("DELETE FROM notification WHERE review_id IS NULL")
    with op.batch_alter_table("notification") as batch_op:
        batch_op.drop_column("message")
        batch_op.drop_column("title")
        batch_op.alter_column(
            "recipe_id",
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=64),
            nullable=False,
        )
        batch_op.alter_column(
            "provider",
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=32),
            nullable=False,
        )
        batch_op.alter_column(
            "review_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )
    op.drop_column("user", "is_admin")
