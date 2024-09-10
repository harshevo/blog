from threading import local
from logger_config import logger
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, insert, update
from starlette.background import BackgroundTask
from blog.auth.crud import check_verification, get_current_user_by_email_or_username
from blog.auth.schemas import UserRegister
from blog.utils.cloudinary import upload_image
from blog.utils.email_verification import send_email_background
from blog.utils.fileuploader import upload_file
from blog.utils.jwt_util import local_jwt
from blog.utils.pw_hash import Hasher
# from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserRegister
from .model import User
from .schemas import UserLogin
from fastapi import Response, BackgroundTasks

#Register
async def create_user(
    background_tasks: BackgroundTasks,
    user: UserRegister,
    profile_picture: UploadFile,
    db: AsyncSession
 ):
    if(
        await get_current_user_by_email_or_username(
            user.email,
            user.username,
            db
        )
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with username or email already exists"
        )

    profile_picture_cloudinary_url = None
    if(profile_picture):
        profile_picture_path = await upload_file(profile_picture)
        if(profile_picture_path is None):
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error Uploading Profile Picture while creating user"
            )
        profile_picture_url = await upload_image(profile_picture_path)
        if(profile_picture_url is None):
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    await _send_verification_email(background_tasks, user.email)
    await db.commit()
    return {"message":"registration complete,email has been sent, please verify your email"}


async def login_user(     #[TODO]verificatio mail isn't being sent to email, i dont know why, need fix
    background_tasks: BackgroundTasks,
    user: UserLogin,
    response: Response,
    db: AsyncSession
) -> Response:
    try:
        existing_user = await db.execute(select(User.id, User.password_hash).where(User.email == user.email))
        user_data = existing_user.first()
        if not user_data:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register to continue."
            )
        user_id, hashed_password = user_data

        if not await check_verification(user.email, db):
            print(f"email: {user.email}")
            await _send_verification_email(background_tasks, user.email)
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not verified. A new verification email has been sent."
            )

        if not Hasher.verify_password(user.password, hashed_password):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials."
            )

        access_token = local_jwt.generate_access_token(str(user_id))
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        response.status_code = status.HTTP_200_OK
        return response

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

async def _send_verification_email(background_tasks: BackgroundTasks, email: str): #TODO: Also pass username into mail to use as Dear username, in template
    try:
        token_email = local_jwt.generate_token_with_email(email)
        
        endpoint_verify = f"http://127.0.0.1:9000/auth/verify-email/{token_email}"
        data = {
            'app_name': "blogify",
            'activate_url': endpoint_verify
        }
        subject = f"Account Verification - blogify"
        
        await send_email_background(
            background_tasks,
            [email],
            subject=subject,
            context=data, 
            template_name="verification.html"
        )
    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send verification email: {str(e)}"
        )


#verify email
async def verify_user_email(token: str, db: AsyncSession):
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found 'or' verification token has expired"
        )
    await db.commit()

    return {
        "status": "success" 
    }







