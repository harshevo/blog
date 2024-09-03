from sqlalchemy import select
from db import get_db
from .model import User

async def get_current_user_by_email(
        email: str,
        db = get_db
):
    stmt = select(User.username).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if(not user):
       return None
    return user

async def get_current_user_by_username(
   username: str, 
   db = get_db
):
   stmt = select(User.username).where(User.username == username)
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

