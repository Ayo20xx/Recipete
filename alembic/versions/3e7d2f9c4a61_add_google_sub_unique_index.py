"""Add a unique index for linked Google identities.

Revision ID: 3e7d2f9c4a61
Revises: a01488ea864a
"""
from typing import Sequence, Union

from alembic import op


revision: str = "3e7d2f9c4a61"
down_revision: Union[str, Sequence[str], None] = "a01488ea864a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_user_google_sub",
        "user",
        ["google_sub"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_user_google_sub", table_name="user")
