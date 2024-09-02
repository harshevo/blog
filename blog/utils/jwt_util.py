import os
import time
from fastapi import HTTPException
import jwt
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 
ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

def generate_access_token(user_id: str) -> Optional[str]: 
    try:
        payload = {
            "user_id": user_id,
            "expires": time.time() + REFRESH_TOKEN_EXPIRE_MINUTES
        }
        token = jwt.encode(payload, "secret", algorithm=ALGORITHM)
        return token
    except Exception as e:
        print(f"cannot generate access token: {e}")
        return None

def verify_token(token: str) -> Dict[str, Any]:
    decoded_token = jwt.decode(token, "secret", algorithms=[ALGORITHM])

    if not isinstance(decoded_token, dict):
        raise HTTPException(status_code=400, detail="Invalid Token Structure")

    return decoded_token

