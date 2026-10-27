from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email : EmailStr
    password : str =Field(min_length=8)

    @field_validator("password")
    @classmethod
    def byte_checker(cls, value:str):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("more than 72 bytes")
        return value


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
