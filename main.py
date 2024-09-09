import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from blog.auth.route import router as auth_router
from blog.posts.route import router as blog_router
from dotenv import load_dotenv
import uvicorn

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(blog_router, tags=["blog"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
