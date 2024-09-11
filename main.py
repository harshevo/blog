from logger_config import setup_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from blog.auth.route import router as auth_router
from blog.posts.route import router as blog_router
from blog.likes.route import router as like_router
from blog.comments.route import router as comment_router
from blog.categories_tags.route import router as category_tag_router
from dotenv import load_dotenv
import uvicorn

load_dotenv()

logger = setup_logger("BlogProject", debug=True) 

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
app.include_router(like_router, tags=["like"])
app.include_router(comment_router, tags=["comment"])
app.include_router(category_tag_router, tags=["category_tag"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
