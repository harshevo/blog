from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator, ValidationError 
from typing import Optional
import re

class UserRegister(BaseModel):
    """
    Schema for user registration with comprehensive input validation.
    """
    fullname: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    bio_txt: Optional[str] = Field(None, max_length=500)
    

    @validator('fullname')
    def validate_fullname(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError('Full name must contain only letters and spaces')
        return v.title()

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @classmethod
    def as_form(
        cls,
        fullname: str = Form(...),
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        bio_txt: Optional[str] = Form(None)
    ):
        try:
            # Create instance and run all validators
            user = cls(
                fullname=fullname,
                username=username,
                email=email,
                password=password,
                bio_txt=bio_txt
            )
            return user
        except ValidationError as e:
            # Convert validation errors to a list of error messages
            error_messages = []
            for error in e.errors():
                error_messages.append(f"{error['loc'][0]}: {error['msg']}")
            raise HTTPException(status_code=422, detail=error_messages)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "username": "john_doe",
                "email": "john@example.com",
                "password": "StrongP@ss123",
                "bio_txt": "Hello, I'm John!"
            }
        }

class UserLogin(BaseModel):
    email: str
    password: str
                
    
