from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int
    author_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True