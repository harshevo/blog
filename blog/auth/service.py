from fastapi import HTTPException, UploadFile 
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy import select, insert
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from blog.auth.schemas import UserRegister
from blog.utils.cloudinary import upload_image
from blog.utils.fileuploader import upload_file
from blog.utils.jwt_util import generate_access_token, verify_token
from blog.utils.pw_hash import Hasher
from db import get_db
from .schemas import UserRegister
from .model import User
from .schemas import UserLogin
from fastapi import Response, Request

#Register
async def create_user(user: UserRegister,profile_picture: UploadFile, db = get_db):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if(existing_user):
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


#Login
async def login_user(user: UserLogin, response: Response, db = get_db):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    print(existing_user)

    if(not existing_user):
        return HTTPException(status_code=400, detail="User does not exist, please register to continue")

    isPasswordCorrect = Hasher.verify_password(user.password, existing_user.password_hash)

    if(isPasswordCorrect == False):
        return HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Password is incorrect")

    accessToken = generate_access_token(str(existing_user.id))

    RedirectResponse("/")

    return response.set_cookie(key="access_token", value=str(accessToken))


#get_user
async def get_current_user(request: Request, db = get_db):
    token = request.cookies.get("access_token")
    decoded_token = verify_token(str(token))

    if(not decoded_token):
        return HTTPException(status_code=400, detail = "Invalid Token")

    user_id = decoded_token.get("user_id")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    return user

