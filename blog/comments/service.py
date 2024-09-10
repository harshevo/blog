import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from .model import Comment
from .schemas import CommentCreate 
from db import get_db

async def create_comment(comment_data: CommentCreate, db = get_db ):
    print(f"blogid: {comment_data.blog_id}, user_id: {comment_data.user_id}")

    try:
        new_comment = Comment(
            content=comment_data.content,
            blog_id=comment_data.blog_id,
            user_id=comment_data.user_id,
            parent_id=comment_data.parent_id 
        )

        db.add(new_comment)
        await db.commit()
        return {"Message": "Successfully Created Comment"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Creating Comment - {e}"
          )

async def get_comments_by_blog(blog_id: uuid.UUID, db=get_db) :
  try:
      result = await db.execute(
          select(Comment)
          .where(Comment.blog_id == blog_id)
          .options(joinedload(Comment.replies)) #--> [JoinedLoad fetches all data with one request]
                                                #    should not be used if the incoming data is large
      )
      comments = result.scalars().all()
      return comments
  except Exception as e:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Error Fetching Comments- {e}"
      )

async def get_comment(comment_id: uuid.UUID, db =  get_db): #Testing and Route Creation - X
  try:
      result = await db.execute(
          select(Comment)
          .where(Comment.id == comment_id)
        )
      comment = result.scalar_one_or_none()
      if not comment:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="Comment not found"
            )
      return comment
  except Exception as e:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"Error fetching Comment - {e}"
      )

async def delete_comment(comment_id: uuid.UUID, db = get_db):#Testing and Route Creation -  X
  try:
    comment = await get_comment(comment_id, db)
    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}
  except Exception as e:
     raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Error deleting Comment - {e}"
     )

#Update Comment Service - X