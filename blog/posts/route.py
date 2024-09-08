import json
from sqlalchemy.ext.asyncio import AsyncSession
from blog.posts.crud import get_all_blogs
from blog.posts.schemas import PostCreate
from blog.posts.service import create_posts
from db import get_db
from ..auth.middlewares import get_current_super_admin
from fastapi import APIRouter, Depends, UploadFile, File
from ..utils.fileuploader import upload_file as upload_file_local
from ..utils.cloudinary import upload_image
router  = APIRouter()

@router.post("/blog")
async def posts(
        blog: PostCreate,
        db: AsyncSession = Depends(get_db),
        curr_user_id = Depends(get_current_super_admin)
): return await create_posts(blog, curr_user_id, db)


@router.get("/blog")
async def get_blogs(db: AsyncSession = Depends(get_db)):
    return await get_all_blogs(db)

@router.post("/upload")
async def upload_file(
        file: UploadFile = File(...)
): 
    file_path = await upload_file_local(file)
    file_url = await upload_image(file_path)
    return file_url
