import uuid
import datetime
from blog.posts.schemas import PostCreate
from .model import Posts
from fastapi import HTTPException, File, UploadFile, status
from sqlalchemy import insert, select, update, exists, delete
from sqlalchemy.ext.asyncio import AsyncSession
from blog.posts import schemas as blog_schemas
from . import model
from ..utils.fileuploader import upload_file as upload_file_local
from ..utils.cloudinary import upload_image


async def create_blog(
        blog: PostCreate,
        user_id: uuid.UUID,
        db: AsyncSession
):
    try:
        db_post = Posts(
            author_id=user_id,
            title=blog.title,
            content=blog.content,
            summary=blog.summary,
            status=blog.status,
            published_at=datetime.datetime.utcnow(),          #Remove this published_at null by default
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.add(db_post)
        await db.commit()
        return {"message": "Blog created successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create blog: {str(e)}"
        )

async def get_all_blogs(
    db: AsyncSession
):
    try:
        stmt = select(Posts)
        result = await db.execute(stmt)
        blogs = result.scalars().all()
        return blogs
    except Exception as e:
        raise HTTPException(    
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def get_blog_by_id(
    blog_id: uuid.UUID,
    db: AsyncSession
):
    try:    
        stmt = select(Posts).where(Posts.id == blog_id)
        result = await db.execute(stmt)
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
        return blog
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


async def get_blogs_by_user(
    user_id: uuid.UUID,
    db: AsyncSession
):
    try:
        stmt = (
            select(Posts)
            .where(Posts.author_id == user_id)
            .where(Posts.status == model.statusEnum.PUBLISHED)
            .order_by(Posts.published_at.desc())
        )                                                               #TODO:use published_at instead of created_at
        result = await db.execute(stmt)
        blogs = result.scalars().all()
        return blogs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def update_blog(
    blog_id: uuid.UUID,
    body: blog_schemas.UpdateBlog,
    db: AsyncSession
):
    stmt = await db.execute(select(exists().where(Posts.id == blog_id)))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    try:
        stmt = update(Posts).where(Posts.id == blog_id).values(body.dict())
        await db.execute(stmt)
        await db.commit()
        return {"message": "Updated Successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error while updating blog: {blog_id}"
        )
    
async def delete_blog(
    blog_id: uuid.UUID,
    db: AsyncSession
):
    stmt = await db.execute(select(exists().where(Posts.id == blog_id)))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    try:
        stmt = delete(Posts).where(Posts.id == blog_id)
        await db.execute(stmt)
        await db.commit()
        return {"message": "Deleted Successfully"}
    except Exception as e:
        await db.rollback()
        #TODO:log this error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error while deleting blog: {blog_id}"
        )
    
async def upload_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile,
    db: AsyncSession
):
    file_path = await upload_file_local(image)
    image_url = await upload_image(file_path)
    stmt = update(Posts).where(Posts.id == blog_id).values(image=image_url)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Uploaded Successfully"}