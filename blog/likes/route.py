from inspect import currentframe
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from blog.likes.service import like_blog
from db import get_db
from ..auth.middlewares import get_current_user

from blog.likes.schemas import Like

router = APIRouter()

@router.post("/like")
async def like(
        like: Like,
        curr_user_id = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        return await like_blog(like, curr_user_id, db)
