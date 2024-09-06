from fastapi import Form
from pydantic import BaseModel, Json

class PostCreate(BaseModel):
    title: str
    slug: str | None=None
    content: dict
    excerpt: str
    
    # @classmethod
    # def as_form(
    #     cls, title: str = Form(...),
    #     slug: str= Form(None),
    #     content: str= Form(...),
    #     excerpt:str =Form(None)
    # ):
    #     return cls(
    #         title= title,
    #         slug= slug,
    #         content = content,
    #         excerpt= excerpt 
    #     )


                
    
