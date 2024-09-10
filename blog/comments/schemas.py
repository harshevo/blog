# schemas.py
import uuid
from pydantic import BaseModel, Field
from typing import Optional

class CommentCreate(BaseModel):
    content: str
    blog_id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None


