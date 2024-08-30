from cloudinary.uploader import UPLOAD_LARGE_CHUNK_SIZE, upload, upload_image
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.background import P
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from db import get_db
from ..utils.cloudinary import upload_image 
from ..utils.fileuploader import upload_file 
import os

# from auth import schemas as user_schema
# from auth.model import User
router = APIRouter()

# @router.post("/register")
# async def register_user(user: auth_schemas.User, db: AsyncSession = Depends(get_db)):
#     return create_user(user, db)
#


# @router.post("/login")
# async def login(user: auth_schemas.User, db: AsyncSession = Depends(get_db)):
#     data = User(username=user.username, password=user.password)
#     db.add(data)
#     await db.commit()
#     await db.refresh(data)
#     return data

@router.post("/upload")
async def handle_upload(image: UploadFile):
    try:
        path = await upload_file(image)
        cwd = os.getcwd()
        os.path.join(f"{cwd}/images")
        print(path)
        url = await upload_image(path)
        print(url)
        return {
            "data": {
                "url": url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading image{e}")


        


