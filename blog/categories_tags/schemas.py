from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class Category(CategoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CategoryWithUser(Category):
    user: "User"

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)

class Tag(TagBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TagWithUser(Tag):
    user: "User"

class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str

    class Config:
        orm_mode = True

CategoryWithUser.update_forward_refs()
TagWithUser.update_forward_refs()

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str]

class Post(PostBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    categories: List[Category] = []
    tags: List[Tag] = []

    class Config:
        orm_mode = True