import json
from sqlalchemy.ext.asyncio import AsyncSession
from blog.posts.crud import get_all_blogs
from blog.posts.schemas import PostCreate
from blog.posts.service import create_posts
from db import get_db
from ..auth.middlewares import is_authorized
from fastapi import APIRouter, Depends, UploadFile, File

router  = APIRouter()

@router.post("/blog")
async def posts(
        blog: PostCreate,
        db: AsyncSession = Depends(get_db),
        curr_user_id = Depends(is_authorized)
): return await create_posts(blog, curr_user_id, db)


@router.get("/blog")
async def get_blogs(db: AsyncSession = Depends(get_db)):
    return await get_all_blogs(db)

