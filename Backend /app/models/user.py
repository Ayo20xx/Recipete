from datetime import datetime, timezone  # noqa: N999
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str | None = None 
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    google_sub: str | None  = None 

    
    