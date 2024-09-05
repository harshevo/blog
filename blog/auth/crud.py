from fastapi import HTTPException
from sqlalchemy import delete, or_, select, or_
from starlette.status import HTTP_400_BAD_REQUEST
from db import get_db
from .model import User

async def get_current_user_by_email_or_username(
        email: str | None,
        username: str | None,
        db = get_db
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
    user_id : str,
    db = get_db,
 ):
    stmt = select(User.username).where(User.id == user_id)
    result = await db.execute(stmt)
    current_user = result.scalar_one_or_none()
    if(not current_user):
      return None
    return current_user

async def get_all_users(
      db = get_db
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
      email,
      db = get_db
):
   stmt = select(User.is_verified).where(User.email == email)
   result = await db.execute(stmt)
   is_verified = result.scalar_one_or_none()
   return is_verified


async def delete_current_user(user_id: str, db = get_db):
   print(user_id)
   try:
      stmt = delete(User).where(User.id == user_id)
      await db.execute(stmt)
      await db.commit()
   except:
      return HTTPException(
         status_code=HTTP_400_BAD_REQUEST,
         detail="Unable to delete User"
      )
