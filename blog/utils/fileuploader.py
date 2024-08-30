from datetime import datetime
from fastapi import File, UploadFile, HTTPException
import os

from starlette.types import HTTPExceptionHandler

UPLOAD_DIR = "images"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def upload_file(file: UploadFile = File(...)):
    timestamp =  datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename= f"{timestamp}_{file.filename}".replace(" ", "-")

    file_path = os.path.join(UPLOAD_DIR, new_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Failed to save the file: {str(e)}")
    
    return file_path





    
        
