from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from auth import schemas as auth_schemas
from auth.model import User
router = APIRouter()

@router.post("/login")
async def login(user: auth_schemas.User, db: AsyncSession = Depends(get_db)):
    data = User(username=user.username, password=user.password)
    db.add(data)
    await db.commit()
    await db.refresh(data)
    return data