"""SQLModel metadata used by models and Alembic."""

from sqlmodel import SQLModel

# Import models so their tables are registered in SQLModel metadata.
from app.models.user import User

metadata = SQLModel.metadata
