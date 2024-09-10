import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from blog.comments.schemas import CommentCreate
from blog.comments.service import create_comment, get_comments_by_blog
from db import get_db

router = APIRouter()

@router.get("/comments")
async def get_comments(blog_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await get_comments_by_blog(blog_id, db)

@router.post("/comments/create")
async def comment_create(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    return await create_comment(comment, db)
