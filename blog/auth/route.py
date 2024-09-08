from threading import local
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, File, Request, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import request
from blog.auth.crud import delete_current_user, get_all_users
from blog.auth.middlewares import get_current_user, get_current_super_admin
from blog.utils.jwt_util import local_jwt
from db import get_db
from .schemas import UserLogin, UserRegister
from .schemas import UserRegister
from .service import create_user, login_user, verify_user_email

router = APIRouter()

@router.post("/register")
async def register_user(
    background_tasks: BackgroundTasks,
    user: UserRegister = Depends(UserRegister.as_form),
    image: UploadFile = File(None), 
    db: AsyncSession = Depends(get_db) 
):
    return await create_user(background_tasks,user, image,  db)

@router.post("/users/token")
async def login(
    background_tasks: BackgroundTasks,
    user: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    return await login_user(background_tasks, user, response, db)

@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    dep = Depends(get_current_user)
): 
    response.delete_cookie("access_token")
    return {"sucess": "200"}

@router.delete("/user")
async def delete_user(
        request: Request,
        response: Response,
        dep = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    decoded_token = local_jwt.verify_token(str(token))
    user_id = decoded_token.get("user_id")
    await delete_current_user(str(user_id), db)
    response.delete_cookie("access_token")
    return {"success": "200"}


@router.get("/verify-email/{token_email}")
async def verify_email(
    token_email: str, db:AsyncSession = Depends(get_db)
):
    return await verify_user_email(token_email, db)

@router.get("/users")
async def get_users(
        request: Request,
        user_id = Depends(get_current_super_admin),
        db:AsyncSession = Depends(get_db)   
): return await get_all_users(db)

    
@router.get("/test-user")
async def test_user(request: Request,
                    user_id = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return request.state.user_id
    
@router.get("/test-super-admin")
async def test_super_admin(request: Request,
                    user_id = Depends(get_current_super_admin), db: AsyncSession = Depends(get_db)):
    return request.state.user_id