from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserProfileBase(BaseModel):
    full_name: str = Field(..., example="Jane Doe")
    financial_literacy_level: str = Field(default="beginner", example="intermediate")

class UserProfile(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "full_name": "Jane Doe",
                "financial_literacy_level": "intermediate",
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-27T10:00:00Z"
            }
        }

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, example="Jane Smith")
    financial_literacy_level: Optional[str] = Field(None, example="expert")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Smith",
                "financial_literacy_level": "expert"
            }
        }

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="strongpassword123")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "full_name": "Jane Doe",
                    "financial_literacy_level": "intermediate",
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z"
                }
            }
        }
