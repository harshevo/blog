from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from sqlalchemy import select
from .model import User, PowerRole as Role
from .crud import get_user_by_id
from ..utils.jwt_util import local_jwt
from db import get_db


async def get_current_user(       # get_current_user
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception
        decoded_token = local_jwt.verify_token(token)
        user_id: str = decoded_token.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id, db)
    if user is None:
        raise credentials_exception

    request.state.user_id = user_id
    return user_id


async def get_current_super_admin(        # get_current_super_admin
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception
        decoded_token = local_jwt.verify_token(token)
        user_id: str = decoded_token.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(User.role).where(User.id == user_id)
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()
    if user_role is not Role.SUPER_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.state.user_id = user_id

    return user_id