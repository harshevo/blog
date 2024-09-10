import uuid
from fastapi import HTTPException
from sqlalchemy import delete, or_, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from db import get_db     # remving this line will cause circular import error
from .model import User

async def get_current_user_by_email_or_username(
   email: str | None,
   username: str | None,
   db: AsyncSession
):
    stmt = select(User.username).where(
     or_(
         User.email == email,
         User.username == username
      )
   )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if(not user):
       return None
    return user


async def get_user_by_id(
   user_id : uuid.UUID,
   db: AsyncSession,
 ):
    stmt = select(User.username).where(User.id == user_id)
    result = await db.execute(stmt)
    current_user = result.scalar_one_or_none()
    if(not current_user):
      return None
    return current_user

async def get_all_users(
   db: AsyncSession
):
   stmt = select(User)
   result = await db.execute(stmt)
   users = result.scalars().all()
   return [{
      "User Name": user.username,
      "Full Name": user.fullname, 
      "Email ID": user.email,
      "Profile Picture": user.profile_picture_url, 
      "Bio": user.bio_txt
   } for user in users]

async def check_verification(
   email: str,
   db: AsyncSession
):
   try:
      stmt = select(User.is_verified).where(User.email == email)
      result = await db.execute(stmt)
      is_verified = result.scalar_one_or_none()
      return is_verified
   except:
      return HTTPException(
         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
         detail="Error While checking verification  - {e}"
      )


async def delete_current_user(
   user_id: uuid.UUID, 
   db: AsyncSession
):
   print(user_id)
   try:
      stmt = delete(User).where(User.id == user_id)
      await db.execute(stmt)
      await db.commit()
   except:
      return HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST,
         detail="Unable to delete User"
      )
