from fastapi import HTTPException, UploadFile, File, status
from sqlalchemy import select, insert
from sqlalchemy.sql.expression import ExpressionClauseList
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from blog.auth.schemas import UserRegister
from blog.utils.cloudinary import upload_image
from blog.utils.fileuploader import upload_file
from blog.utils.pw_hash import Hasher
from db import get_db
from .schemas import UserRegister
from .model import User

async def create_user(user: UserRegister,profile_picture: UploadFile, db = get_db):
    stmt = select(User.email).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if(existing_user is not None):
        return HTTPException(status_code=HTTP_400_BAD_REQUEST, detail = "User already Exists")

    profile_picture_path = await upload_file(profile_picture)

    if(profile_picture_path is None):
        return HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Uploading Profile Picture while creating user")
    
    profile_picture_url = await upload_image(profile_picture_path)
    
    if(profile_picture_url is None):
        return HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading profile picture to cloudinary")

    
    hashed_password = ""
    if(user.password):
        hashed_password = Hasher.get_password_hash(user.password)
    
    
    insert_stmt = insert(User).values(
        fullname = user.fullname,
        username = user.username,
        email = user.email,
        password_hash = hashed_password,
        profile_picture_url = profile_picture_url,
        bio_txt = user.bio_txt
    )
    
    await db.execute(insert_stmt)
    await db.commit()
    
    return user;
