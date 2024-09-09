# import json
# from .model import Blog
# from db import get_db
# from sqlalchemy import select

# async def get_all_blogs(db = get_db):
#     stmt = select(Blog)
#     result = await db.execute(stmt)
#     all_blogs = result.scalar_one_or_none()
#     return all_blogs


