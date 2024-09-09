import uuid
import datetime
from blog.posts.schemas import PostCreate
from blog.posts import schemas as blog_schemas
from .model import Blog, BlogImage, statusEnum
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, update, exists, delete, func
from ..utils.fileuploader import upload_file as upload_file_local
from ..utils.cloudinary import upload_image, delete_image_from_cloudinary

def set_values(values: dict, List: list):
    for row in values:
        post = row.Posts
        post_dict = {
            "id": str(post.id),
            "title": post.title,
            "author_id": str(post.author_id),
            "image_url": post.image_url,
            "slug": post.slug,
            "summary": post.summary,
            "status": post.status.value,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
            "total_likes": row.total_likes,
            "total_views": row.total_views
        }
        List.append(post_dict)

async def create_blog(
        blog: PostCreate,
        user_id: uuid.UUID,
        db: AsyncSession
):
    try:
        db_post = Blog(
            author_id=user_id,
            title=blog.title,
            content=blog.content,
            summary=blog.summary,
            status=blog.status,
            published_at=datetime.datetime.utcnow(),          #TODO:Remove this published_at null by default
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
    filter: statusEnum,
    db: AsyncSession
):
    try:
        stmt = (
            select(
                Blog, 
                func.coalesce(BlogImage.image_url, None).label('image_url')    #Used func.coalesce() to handle NULL values for image_url
            )
            .outerjoin(
                BlogImage, 
                Blog.id == BlogImage.blog_id
            )
            .where(Blog.status == filter)
            .order_by(Blog.created_at.desc())
        )
        result = await db.execute(stmt)
        return [
            blog_schemas.BlogResponse(
                **{k: v for k, v in blog.__dict__.items() if not k.startswith('_')},   #just extracting values of dict in key(k), vlaue(v) pair same as **blog.__dict__
                image_url=image_url
            )
            for blog, image_url in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching blogs: {str(e)}"
        )


async def get_blog_by_id(
    blog_id: uuid.UUID,
    db: AsyncSession
) -> blog_schemas.BlogResponse:
    try:    
        stmt = (
            select(Blog, BlogImage.image_url)
            .outerjoin(BlogImage, Blog.id == BlogImage.blog_id)
            .where(Blog.id == blog_id)
        )
        result = await db.execute(stmt)
        blog, image_url = result.one_or_none()
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        return blog_schemas.BlogResponse(
            **blog.__dict__,
            image_url=image_url
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the blog: {str(e)}"
        )


async def get_blogs_by_user(
    user_id: uuid.UUID,
    filter: statusEnum,
    db: AsyncSession
):
    try:
        stmt = (
            select(
                Blog, 
                func.coalesce(BlogImage.image_url, None).label('image_url')    #Used func.coalesce() to handle NULL values for image_url
            )
            .outerjoin(
                BlogImage, 
                Blog.id == BlogImage.blog_id
            )
            .where(Blog.status == filter)
            .where(Blog.author_id == user_id)
            .order_by(Blog.created_at.desc())
        )
        result = await db.execute(stmt)
        return [
            blog_schemas.BlogResponse(
                **{k: v for k, v in blog.__dict__.items() if not k.startswith('_')},   #just extracting values of dict in key(k), vlaue(v) pair same as **blog.__dict__
                image_url=image_url
            )
            for blog, image_url in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching User's blogs: {str(e)}"
        )


async def update_blog(
    blog_id: uuid.UUID,
    body: blog_schemas.UpdateBlog,
    db: AsyncSession
):
    stmt = await db.execute(select(exists().where(Blog.id == blog_id)))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    try:
        stmt = update(Blog).where(Blog.id == blog_id).values(body.dict())
        await db.execute(stmt)
        await db.commit()
        return {"message": "Updated Successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error while updating blog: {blog_id}"
        )


async def update_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile,
    db: AsyncSession
):
    # delete the associated image from cloudinary
    # delete the associated image from the database
    # upload the new image to cloudinary
    # save the image url to the database with the blog_id
    pass
        


async def delete_blog(
    blog_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
):
    # Check if the blog exists and belongs to the user
    stmt = select(exists().where(Blog.id == blog_id).where(Blog.author_id == user_id))
    result = await db.execute(stmt)
    if not result.scalar_one():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    # Get the associated image
    stmt = select(BlogImage).where(BlogImage.blog_id == blog_id)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()

    if image:
        try:
            await delete_image_from_cloudinary(image.image_url)
            await db.delete(image)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting image from cloudinary: {str(e)}"
            )

    try:
        # Delete the blog
        stmt = delete(Blog).where(Blog.id == blog_id)
        await db.execute(stmt)
        await db.commit()
        return {"message": "Deleted Successfully"}
    except Exception as e:
        await db.rollback()
        # TODO: log this error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error while deleting blog: {str(e)}"
        )

    
async def upload_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile,
    db: AsyncSession
):
    try:
        file_path = await upload_file_local(image)
        image_url = await upload_image(file_path)
        url = BlogImage(blog_id=blog_id, image_url=image_url)
        db.add(url)
        await db.commit()
        await db.refresh(url)
        return url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while uploading image: {str(e)}"
        )
    
async def set_status(
    blog_id: uuid.UUID,
    status: statusEnum,
    db: AsyncSession
):
    try:
        stmt = update(Blog).where(Blog.id == blog_id).values(status=status)
        await db.execute(stmt)
        await db.commit()
        return {"message": "Status updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while updating status: {str(e)}"
        )


