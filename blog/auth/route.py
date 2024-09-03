from fastapi import APIRouter, BackgroundTasks, Depends, File, Request, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from blog.auth.crud import get_all_users
from blog.auth.middlewares import is_authorized
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

@router.post("/login")
async def login(
    user: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    return await login_user(user, response, db)

@router.get("/verify-email/{token_email}")
async def verify_email(
    token_email: str, db:AsyncSession = Depends(get_db)
):
    return await verify_user_email(token_email, db)

@router.get("/users")
async def get_users(
        request: Request,
        dependencies = Depends(is_authorized),
        db:AsyncSession = Depends(get_db)
): return await get_all_users(db) 
    

    

