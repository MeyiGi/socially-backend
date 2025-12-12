from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: Optional[str]
    username: str
    email: str
    image: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    website: Optional[str]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    image: Optional[str] = None