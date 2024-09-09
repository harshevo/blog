import uuid
from pydantic import BaseModel

class Like(BaseModel):
    blog_id: uuid.UUID
    

