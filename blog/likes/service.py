import uuid
from starlette import status
from blog.likes.model import BlogLikes
from .schemas import Like
from db import get_db
from sqlalchemy import select, delete, and_
from fastapi import HTTPException
from ..posts.model import Blog

async def like_blog(
        like: Like,
        current_user_id: uuid.UUID,
        db = get_db
):
    try: 
        post_exists = await db.scalar(
            select(Blog.id).where(Blog.id == like.blog_id)
        )    
        if(not post_exists):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post Not Found."
            )

        existing_like_stmt = await db.execute(
                select(BlogLikes)
                    .where(
                    and_(
                        BlogLikes.blog_id== like.blog_id,
                        BlogLikes.user_id == current_user_id
                    )))
        existing_like = existing_like_stmt.scalars().first()
        if(existing_like):
            delete_stmt = (delete(BlogLikes)
                        .where(
                        and_(
                            BlogLikes.blog_id == like.blog_id,
                            BlogLikes.user_id == current_user_id
                        )))
            await db.execute(delete_stmt)
            await db.commit()
            return {"Message": "Post DisLiked"}


        update_stmt = BlogLikes(
                    blog_id = like.blog_id,
                    user_id = current_user_id
                )

        db.add(update_stmt)
        await db.commit()

        return {"Message": "Blog Liked"}
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Processing Like - {e}"
        )
