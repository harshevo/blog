from datetime import UTC, datetime, timedelta
import time
import jwt
import os
from fastapi import HTTPException
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

REFRESH_TOKEN_EXPIRE_SECONDS= 60 * 24 * 7 
ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

class local_jwt:
    @staticmethod
    def generate_access_token(user_id: str) -> Optional[str]: 
        try:
            payload = {
                "user_id": user_id,
                "exp": datetime.now(tz=UTC) + timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
            }
            token = jwt.encode(payload, str(JWT_SECRET), algorithm=ALGORITHM)
            return token
        except Exception as e:
            print(f"cannot generate access token: {e}")
            return None

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            decoded_token = jwt.decode(token, str(JWT_SECRET), algorithms=[ALGORITHM])
            if not isinstance(decoded_token, dict):
                raise HTTPException(status_code=400, detail="Invalid Token")
            return decoded_token
        except jwt.ExpiredSignatureError:
            return {"status_code": 401, "detail": "token expired"}
            

    @staticmethod
    def generate_token_with_email(email: str) -> Optional[str]:
        try: 
            payload = {
                "email": email,
                "exp": datetime.now(tz=UTC) + timedelta(seconds=300)
            }
            token = jwt.encode(payload, str(JWT_SECRET), algorithm=ALGORITHM)
            print(token)
            return token
        except Exception as e:
            print(f"cannot generate access token: {e}")
            return None
