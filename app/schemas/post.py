from pydantic import BaseModel
from typing import Optional, List
from .user import UserOut

class PostCreate(BaseModel):
    content: str
    image: Optional[str] = None

class CommentCreate(BaseModel):
    content: str