from pydantic import BaseModel, EmailStr,Field,field_validator


class UserCreate(BaseModel):
    email : EmailStr
    password : str =Field(min_length=8)

    
