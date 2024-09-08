import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from blog.posts.crud import get_all_blogs
from blog.posts import service as post_service
from db import get_db
from ..auth.middlewares import get_current_user
from fastapi import APIRouter, Depends, UploadFile, File, Request
from ..utils.fileuploader import upload_file as upload_file_local
from ..utils.cloudinary import upload_image
from blog.posts import schemas as blog_schemas
router  = APIRouter()


# Create
@router.post("/blog")
async def create_blog(
        blog: blog_schemas.PostCreate,
        db: AsyncSession = Depends(get_db),
        curr_user_id = Depends(get_current_user)
): 
    return await post_service.create_blog(blog, curr_user_id, db)

# Get
@router.get("/blog")
async def get_blogs(
    db: AsyncSession = Depends(get_db)
):  
    return await post_service.get_all_blogs(db)

@router.get("/blog/user")
async def get_blogs_by_user(
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.get_blogs_by_user(user_id, db)

# GET BY ID
@router.get("/blog/{blog_id}")
async def get_blog(
    blog_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await post_service.get_blog_by_id(blog_id, db)


@router.put("/blog/{blog_id}")
async def update_blog(
    blog_id: uuid.UUID,
    body: blog_schemas.UpdateBlog,
    db: AsyncSession = Depends(get_db)
):
    return await post_service.update_blog(blog_id, body, db)

@router.delete("/blog/{blog_id}")
async def delete_blog(
    blog_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await post_service.delete_blog(blog_id, db)

# @router.post("/blog/upload")
# async def upload_file(
#         file: UploadFile = File(...)
# ): 
#     file_path = await upload_file_local(file)
#     file_url = await upload_image(file_path)
#     return file_url


@router.post("/blog/{blog_id}/upload-image")
async def upload_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.upload_blog_image(blog_id, image, db, user_id)
