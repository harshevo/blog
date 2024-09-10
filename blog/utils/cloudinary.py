import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

# CLOUDINARY
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

async def upload_image(local_file_path):
    try:
        upload_result = cloudinary.uploader.upload(
                    local_file_path,
                    use_filename = True,
                    uinque_filename = True,
                )
        file_url = upload_result.get("secure_url")
        if(file_url):
            os.remove(local_file_path)
        return file_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading images: {e}"
        )

async def delete_image_from_cloudinary(image_url):
    try:
        public_id = "/".join(image_url.split("/")[-1:]).split(".")[0]
        result = cloudinary.uploader.destroy(public_id, invalidate=True)
        if result.get('result') == 'ok':
            print(f"Image deleted successfully: {public_id}")
        else:
            print(f"Failed to delete image: {public_id}")
            raise Exception("Image deletion failed")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image from cloudinary: {str(e)}"
        )
