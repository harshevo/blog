import datetime
from blog.posts.schemas import PostCreate
from db import get_db
from ..utils.fileuploader import upload_file
from ..utils.cloudinary import upload_image
from .model import Posts
from fastapi import HTTPException, File
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy import insert

async def create_posts(
        blog: PostCreate,
        curr_user_id,
        db = get_db,
):
    # image_cloudinary_url = None
    # if(image):
    #     image_path = await upload_file(image)
    #     if(image_path is None):
    #         return HTTPException(
    #             status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Error Uploading Profile Picture while creating user"
    #         )
    #     image_url = await upload_image(image_path)
    #     if(image_url is None):
    #         return HTTPException(
    #             status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Error uploading profile picture to cloudinary"
    #         )
    #     image_cloudinary_url = image_url
    #
    insert_stmt = insert(Posts).values(
        title = blog.title,
        slug = blog.slug,
        author_id = curr_user_id,
        content = blog.content,
        published_at = datetime.datetime.now(),
        excerpt = blog.excerpt
    )
    await db.execute(insert_stmt)
    await db.commit()
