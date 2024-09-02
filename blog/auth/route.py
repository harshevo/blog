from fastapi import APIRouter, Depends, File, Request, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from .schemas import UserLogin, UserRegister
from .schemas import UserRegister
from .service import create_user, login_user, get_current_user

router = APIRouter()

@router.post("/register")
async def register_user(user: UserRegister = Depends(UserRegister.as_form),image: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    return await create_user(user,image,  db)

@router.post("/login")
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    return await login_user(user, response, db)

@router.get("/user")
async def get_user(request: Request, db: AsyncSession = Depends(get_db)):
    return await get_current_user(request, db)
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

        


