from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def byte_checker(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("more than 72 bytes")
        return value


class UserCreate(UserLogin):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoogleTokenRequest(BaseModel):
    id_token: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
