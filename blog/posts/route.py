import uuid
from db import get_db
from blog.posts.model import statusEnum
from blog.posts import service as post_service
from blog.posts import schemas as blog_schemas
from ..auth.middlewares import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile, File


router  = APIRouter()


# Create
@router.post("/blog")
async def create_blog(
        blog: blog_schemas.PostCreate,
        db: AsyncSession = Depends(get_db),
        curr_user_id = Depends(get_current_user)
): 
    return await post_service.create_blog(blog, curr_user_id, db)

# Upload Image in Blog
@router.post("/blog/{blog_id}/upload-image")
async def upload_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.upload_blog_image(blog_id, image, db)

# Get All Blogs
@router.get("/blog")
async def get_blogs(  
    filter: statusEnum,
db: AsyncSession = Depends(get_db)
) -> list[blog_schemas.BlogResponse]:  
    return await post_service.get_all_blogs(filter, db)


# Get All Blogs by User
@router.get("/blog/user")
async def get_blogs_by_user(
    filter: statusEnum,
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.get_blogs_by_user(user_id, filter, db)


# Get Blog by ID
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


@router.put("/blog/{blog_id}/update-image")
async def update_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.update_blog_image(blog_id, image, db)


@router.delete("/blog/{blog_id}")
async def delete_blog_and_image(
    blog_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.delete_blog(blog_id, user_id, db)

@router.get("/blog/{blog_id}/set-status")
async def set_status(
    blog_id: uuid.UUID,
    status: statusEnum,
    db: AsyncSession = Depends(get_db),
    user_id = Depends(get_current_user)
):
    return await post_service.set_status(blog_id, status, db)