from threading import local
from fastapi import HTTPException, UploadFile
from sqlalchemy import select, insert, update
from starlette.background import BackgroundTask
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED
from blog.auth.crud import check_verification, get_current_user_by_email_or_username
from blog.auth.schemas import UserRegister
from blog.utils.cloudinary import upload_image
from blog.utils.email_verification import send_email_background
from blog.utils.fileuploader import upload_file
from blog.utils.jwt_util import local_jwt
from blog.utils.pw_hash import Hasher
from db import get_db
from .schemas import UserRegister
from .model import User
from .schemas import UserLogin
from fastapi import Response, BackgroundTasks

#Register
async def create_user(
    background_tasks: BackgroundTasks,
    user: UserRegister,
    profile_picture: UploadFile,
    db = get_db
 ):
    if(
        await get_current_user_by_email_or_username(
            user.email,
            user.username,
            db
        )
    ):
        return HTTPException(
            HTTP_404_NOT_FOUND,
            detail="User with username or email already exists"
        )

    profile_picture_cloudinary_url = None
    if(profile_picture):
        profile_picture_path = await upload_file(profile_picture)
        if(profile_picture_path is None):
            return HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Uploading Profile Picture while creating user"
            )
        profile_picture_url = await upload_image(profile_picture_path)
        if(profile_picture_url is None):
            return HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading profile picture to cloudinary"
            )
        profile_picture_cloudinary_url = profile_picture_url

    hashed_password = ""
    if(user.password):
        hashed_password = Hasher.get_password_hash(user.password)

    insert_stmt = insert(User).values(
        fullname = user.fullname,
        username = user.username,
        email = user.email,
        password_hash = hashed_password,
        profile_picture_url = profile_picture_cloudinary_url,
        bio_txt = user.bio_txt
    )

    await db.execute(insert_stmt)
    email = user.email
    token_email = local_jwt.generate_token_with_email(email)
    #need to change the host url
    endpoint_verify = f"127.0.0.1:8000/auth/verify-email/{token_email}"
    await send_email_background(background_tasks, "Blogify", user.email, endpoint_verify)
    await db.commit()
    return {"message":"registration complete,email has been sent, please verify your email"}


#Login
async def login_user(
    background_task: BackgroundTasks,
    user: UserLogin,
    response: Response,
    db = get_db
 ):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if(not existing_user):
        return HTTPException(
            status_code=400,
            detail="User does not exist, please register to continue"
        )

    if((await check_verification(user.email, db)) == False):
        token_email = local_jwt.generate_token_with_email(user.email)
        endpoint_verify = f"127.0.0.1:8000/auth/verify-email/{token_email}"
        await send_email_background(
            background_task,
            "Blogify",
            user.email,
            endpoint_verify
        )
        return HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is not verified, please verify your email,verification email is sent to your email"
        )


    isPasswordCorrect = Hasher.verify_password(user.password, existing_user.password_hash)
    if(isPasswordCorrect == False):
        return HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    accessToken = local_jwt.generate_access_token(str(existing_user.id))
    return response.set_cookie(
        key="access_token",
        value=str(accessToken)
    )


#verify email
async def verify_user_email(token: str, db = get_db):
    decoded_token = local_jwt.verify_token(token)
    user_email = decoded_token.get("email")
    
    stmt = (
        update(User)
            .where(User.email == user_email)
            .values(is_verified = True)
            .execution_options(synchronize_session="fetch")
        )
    result = await db.execute(stmt)
    print(result)
    if(result.rowcount == 0):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="user not found 'or' verification token has expired"
        )
    await db.commit()

    return {
        "status": "success" 
    }







