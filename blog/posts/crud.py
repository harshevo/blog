import json
from .model import Posts
from db import get_db
from sqlalchemy import select

async def get_all_blogs(db = get_db):
    stmt = select(Posts.content)
    result = await db.execute(stmt)
    all_blogs = result.scalar_one_or_none()
    print(type(all_blogs))
    return all_blogs


