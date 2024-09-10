# import uuid
# from typing import List
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import joinedload
# from fastapi import HTTPException, status
# from .model import Comment
# from .schemas import CommentCreate 
# from db import get_db

# async def create_comment(
#       blog_id: uuid.UUID,
#       comment_data: CommentCreate,
#       user_id: uuid.UUID,
#       db = get_db
#     ):
#     print(f"blogid: {blog_id}, user_id: {user_id}")

#     try:
#         new_comment = Comment(
#             content=comment_data.content,
#             blog_id=blog_id,
#             user_id=user_id,
#             parent_id=comment_data.parent_id 
#         )

#         db.add(new_comment)
#         await db.commit()
#         return {"Message": "Successfully Created Comment"}
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error Creating Comment - {e}"
#           )

# async def get_comments_by_blog(blog_id: uuid.UUID, db=get_db) :
#   try:
#       result = await db.execute(
#           select(Comment)
#           .where(Comment.blog_id == blog_id)
#           .options(joinedload(Comment.replies)) #--> [JoinedLoad fetches all data with one request]
#                                                 #    should not be used if the incoming data is large
#       )
#       comments = result.scalars().all()
#       return comments
#   except Exception as e:
#       raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Error Fetching Comments- {e}"
#       )

# async def get_comment(comment_id: uuid.UUID, db =  get_db): #Testing and Route Creation - X
#   try:
#       result = await db.execute(
#           select(Comment)
#           .where(Comment.id == comment_id)
#         )
#       comment = result.scalar_one_or_none()
#       if not comment:
#           raise HTTPException(
#               status_code=status.HTTP_404_NOT_FOUND,
#               detail="Comment not found"
#             )
#       return comment
#   except Exception as e:
#       raise HTTPException(
#           status_code=status.HTTP_404_NOT_FOUND,
#           detail=f"Error fetching Comment - {e}"
#       )

# async def delete_comment(comment_id: uuid.UUID, db = get_db):#Testing and Route Creation -  X
#   try:
#     comment = await get_comment(comment_id, db)
#     await db.delete(comment)
#     await db.commit()
#     return {"message": "Comment deleted successfully"}
#   except Exception as e:
#      raise HTTPException(
#         status_code=status.HTTP_400_BAD_REQUEST, 
#         detail="Error deleting Comment - {e}"
#      )

# #Update Comment Service - X

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .model import Comment
from .schemas import CommentCreate, CommentUpdate
import uuid
from typing import List, Optional
from datetime import datetime
from logger_config import logger
from fastapi import HTTPException
#TODO: do error handling

async def create_comment(blog_id: uuid.UUID, comment: CommentCreate, user_id: uuid.UUID, db: AsyncSession):
    db_comment = Comment(
        content=comment.content,
        blog_id=blog_id,
        user_id=user_id,
        parent_id=comment.parent_id,  # parent id means comment parent id which comment it is connected with
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_comment)
    await db.commit()
    return {"message": "Comment created successfully"}


async def get_comments_by_blog(blog_id: uuid.UUID, db: AsyncSession, skip: int = 0, limit: int = 20):
    query = (
        select(Comment)
        .where(Comment.blog_id == blog_id, Comment.parent_id == None)
        .options(selectinload(Comment.replies))
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_comment_by_id(comment_id: uuid.UUID, db: AsyncSession):
    query = (
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.replies))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_comment(comment_id: uuid.UUID, comment_update: CommentUpdate, user_id: uuid.UUID, db: AsyncSession):
    db_comment = await get_comment_by_id(comment_id, db)
    if db_comment and str(db_comment.user_id) == str(user_id):
        for key, value in comment_update.dict(exclude_unset=True).items():
            setattr(db_comment, key, value)
        db_comment.updated_at = datetime.now()
        await db.commit()
        await db.refresh(db_comment)
        return db_comment
    return None

async def delete_comment(comment_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> bool:
    db_comment = await get_comment_by_id(comment_id, db)
    if db_comment and str(db_comment.user_id) == str(user_id):
        await db.delete(db_comment)
        await db.commit()
        return True
    return False

async def get_comment_replies(comment_id: uuid.UUID, db: AsyncSession, skip: int = 0, limit: int = 20):
    try:
        query = (
            select(Comment)
        .where(Comment.parent_id == comment_id)
        .options(selectinload(Comment.replies))
        .offset(skip)
        .limit(limit)
    )
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")