from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,  Request, HTTPException, status
from jose import JWTError
from db import get_db
from ..utils.jwt_util import local_jwt
from .crud import get_user_by_id
from blog.posts.schemas import PostCreate

async def is_authorized(
        request: Request,
        db:AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if(token is None):
      raise credentials_exception
    try:
       decoded_token = local_jwt.verify_token(str(token))
    except JWTError:
      raise credentials_exception

    user_id = decoded_token.get("user_id")
    user = await get_user_by_id(str(user_id), db)
    if(user is None):
       return credentials_exception

    return user_id
