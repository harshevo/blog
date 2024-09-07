from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,  Request, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from starlette.status import HTTP_200_OK
from .model import User, PowerRole as Role
from db import get_db
from ..utils.jwt_util import local_jwt
from .crud import get_user_by_id
from blog.posts.schemas import PostCreate

async def is_authenticated(
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

    request.state.user_id = user_id
    return user_id
    

async def is_authorized(
    request: Request,
    db: AsyncSession = Depends(get_db)
): 
  user_id = request.state.user_id
  stmt = select(User.role).where(User.id == user_id)
  result = await db.execute(stmt)
  user_role = result.scalar_one_or_none()
  if(user_role is not  Role.SUPER_USER):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="UnAuthorized"
    )

  return 
