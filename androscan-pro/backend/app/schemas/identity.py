from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=256)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str


class AssignRolesRequest(BaseModel):
    role_names: list[str] = Field(min_length=1, max_length=10)


class UserWithRolesResponse(UserResponse):
    roles: list[RoleResponse]
