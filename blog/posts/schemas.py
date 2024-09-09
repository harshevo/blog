from pydantic import BaseModel
from datetime import datetime
from .model import statusEnum
import uuid

class PostCreate(BaseModel):
    title: str
    slug: str | None=None
    content: dict
    summary: str
    status: statusEnum

class UpdateBlog(BaseModel):
    title: str | None
    content: dict | None
    summary: str | None
                
class BlogResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: dict
    image_url: str | None
    summary: str
    status: statusEnum
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
