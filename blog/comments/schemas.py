# schemas.py
import uuid
from pydantic import BaseModel, Field
from typing import Optional

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None


from datetime import datetime
from typing import Optional, List

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    parent_id: Optional[uuid.UUID] = None

class CommentUpdate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: uuid.UUID
    blog_id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    replies: List['CommentResponse'] = []

    class Config:
        orm_mode = True

CommentResponse.update_forward_refs()