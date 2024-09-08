from fastapi import Form
from pydantic import BaseModel, Json
from .model import statusEnum

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
                
    
