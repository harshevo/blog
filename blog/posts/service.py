import uuid
import datetime
import sqlalchemy
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from blog.posts.schemas import PostCreate
from blog.posts import schemas as blog_schemas
from .model import Blog, BlogImage, statusEnum
from ..likes.model import BlogLikes
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, update, exists, delete, func
from ..utils.fileuploader import upload_file as upload_file_local
from ..utils.cloudinary import upload_image, delete_image_from_cloudinary
from logger_config import logger

def set_values(values, List):
    for row in values:
        post = row.Blog
        post_dict = {
            **post.__dict__,
            "total_likes": row.total_likes,
            "image_url": row.image_url
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
        logger.error(f"Error While Creating Blog : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create blog: {str(e)}"
        )


# async def get_all_blogs(
#     filter: statusEnum,
#     db: AsyncSession
# ):
#     try:
#         # stmt = (
#         #     select(
#         #         Blog, 
#         #         func.coalesce(BlogImage.image_url, None).label('image_url'),    #Used func.coalesce() to handle NULL values for image_url
#         #         func.count(BlogLikes.id).label('total_likes')
#         #     )
#         #     .outerjoin(
#         #         BlogImage, 
#         #         Blog.id == BlogImage.blog_id
#         #     )
#         #     .outerjoin(
#         #         BlogLikes,
#         #         Blog.id == BlogLikes.blog_id
#         #     )
#         #     .where(Blog.status == filter)
#         #     .group_by(Blog.id)
#         # )
#         stmt = (
#             select(
#                 Blog, 
#                 func.coalesce(BlogImage.image_url, None).label('image_url'),
#                 func.count(BlogLikes.id).label('total_likes')
#             )
#             .outerjoin(BlogImage, Blog.id == BlogImage.blog_id)
#             .outerjoin(BlogLikes, Blog.id == BlogLikes.blog_id)
#             .where(Blog.status == filter)
#             .group_by(Blog.id, BlogImage.image_url)
#         )
#         result = await db.execute(stmt)
#         return [
#             blog_schemas.BlogResponse(
#                 # **{k: v for k, v in blog.__dict__.items() if not k.startswith('_')},
#                 **blog.__dict__,
#                 image_url=image_url,
#                 total_likes=total_likes
#             )
#             for blog, image_url, total_likes in result
#         ]
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred while fetching blogs: {str(e)}"
#         )
async def get_all_blogs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20
):
    try:
        stmt = (select(
                Blog,
                func.count(BlogLikes.id).label("total_likes"),
                func.coalesce(BlogImage.image_url, None).label('image_url')
            ).outerjoin(
                BlogLikes, Blog.id == BlogLikes.blog_id
            )
            .outerjoin(
                BlogImage, Blog.id == BlogImage.blog_id
            )
            .where(Blog.status == statusEnum.PUBLISHED)
            .group_by(Blog.id, BlogImage.image_url)
            .limit(limit)
            .offset(skip)
        )

        result = await db.execute(stmt)
        blog_with_likes = []
        set_values(result, blog_with_likes)
        return blog_with_likes
    except Exception as e:
        logger.error(f"Error Fetching Blogs: {str(e)}")
        return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error Fetching Blogs: {str(e)}"
                )



async def get_blog_by_id(
    blog_id: uuid.UUID,
    db: AsyncSession
) -> list[blog_schemas.BlogResponse]:
    try:    
        stmt = (select(
                Blog,
                func.count(BlogLikes.id).label("total_likes"),
                func.coalesce(BlogImage.image_url, None).label('image_url')
            ).outerjoin(
                BlogLikes, Blog.id == BlogLikes.blog_id
            )
            .outerjoin(
                BlogImage, Blog.id == BlogImage.blog_id
            )
            .where(Blog.id == blog_id)
            .where(Blog.status == statusEnum.PUBLISHED)
            .group_by(Blog.id, BlogImage.image_url)
        )

        result = await db.execute(stmt)
        blog_with_likes = []
        set_values(result, blog_with_likes)
        return blog_with_likes
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error while fetching blog by blogId: {str(e)}")
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
        stmt = (select(
                Blog,
                func.count(BlogLikes.id).label("total_likes"),
                func.coalesce(BlogImage.image_url, None).label('image_url')
            ).outerjoin(
                BlogLikes, Blog.id == BlogLikes.blog_id
            )
            .outerjoin(
                BlogImage, Blog.id == BlogImage.blog_id
            )
            .where(Blog.status == filter)
            .where(Blog.author_id == user_id)
            .group_by(Blog.id, BlogImage.image_url)
        )

        result = await db.execute(stmt)
        blog_with_likes = []
        set_values(result, blog_with_likes)
        return blog_with_likes
    except Exception as e:
        logger.error(f"Error fetching blogs by user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the blog: {str(e)}"
        )

async def update_blog(
    blog_id: uuid.UUID,
    body: blog_schemas.UpdateBlog,
    db: AsyncSession
):
    try:
        stmt = await db.execute(select(exists().where(Blog.id == blog_id)))
        result = stmt.scalar_one_or_none()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
        stmt = update(Blog).where(Blog.id == blog_id).values(body.dict())
        await db.execute(stmt)
        await db.commit()
        return {"message": "Updated Successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error Updating Blog: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error while updating blog: {blog_id}"
        )


async def update_blog_image(
    blog_id: uuid.UUID,
    image: UploadFile,
    db: AsyncSession
):
    try:
        result = await db.execute(select(BlogImage.image_url).where(BlogImage.blog_id == blog_id))
        existing_image_url = result.scalar_one_or_none()

        if not existing_image_url:
            return HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Image for blog_id does not exists"
                )
       
        await delete_image_from_cloudinary(existing_image_url)

        image_local_path = await upload_file_local(image)
        image_cloudinary_url = await upload_image(image_local_path)

        stmt = update(BlogImage).where(BlogImage.blog_id == blog_id).values(image_url = image_cloudinary_url)
        await db.execute(stmt)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error Updating Blog Image : {str(e)}")
        return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error Updating Image - {e}"
             )


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
        logger.error(f"Error while deleting blog: {str(e)}")
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
        logger.error(f"Error while Uploading Blog Image: {str(e)}")
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
        logger.error(f"Error while Updating Status: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while updating status: {str(e)}"
        )


