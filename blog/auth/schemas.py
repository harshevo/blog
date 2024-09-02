from fastapi import Form
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    fullname: str
    username: str
    email: EmailStr
    password: str
    bio_txt: str
    
    @classmethod
    def as_form(cls, fullname: str = Form(...), username: str = Form(...), email: str= Form(...), password: str = Form(...), bio_txt:str =Form(...)):
        return cls(fullname = fullname, username = username, email = email, password = password, bio_txt = bio_txt)

class UserLogin(BaseModel):
    email: str
    password: str
                
    
