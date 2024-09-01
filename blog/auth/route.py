from cloudinary.uploader import UPLOAD_LARGE_CHUNK_SIZE, upload, upload_image
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.background import P
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from db import get_db
from ..utils.cloudinary import upload_image 
from ..utils.fileuploader import upload_file 
from .schemas import UserLogin, UserRegister
import os

from .schemas import UserRegister
from .service import create_user, login_user
# from auth.model import User
router = APIRouter()

@router.post("/register")
async def register_user(user: UserRegister = Depends(UserRegister.as_form),image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    return await create_user(user,image,  db)

@router.post("/login")
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    return await login_user(user, response, db)

# @router.post("/upload")
# async def handle_upload(image: UploadFile):
#     try:
#         path = await upload_file(image)
#         cwd = os.getcwd()
#         os.path.join(f"{cwd}/images")
#         print(path)
#         url = await upload_image(path)
#         print(url)
#         return {
#             "data": {
#                 "url": url
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading image{e}")
#

        


