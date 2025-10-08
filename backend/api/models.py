from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DocumentMeta(BaseModel):
    id: str = Field(alias="_id")
    owner_id: str
    filename: str
    size: int

class ChatRequest(BaseModel):
    session_id: str
    message: str
    document_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list[dict]] = None


