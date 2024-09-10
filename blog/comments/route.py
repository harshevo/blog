import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from blog.comments.schemas import CommentCreate
from blog.comments.service import create_comment, get_comments_by_blog
from db import get_db
from ..auth.middlewares import get_current_user
# router = APIRouter()

# @router.get("/blogs/{blog_id}/comments")
# async def get_comments(blog_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
#     return await get_comments_by_blog(blog_id, db)

# @router.post("/blogs/{blog_id}/comments")     #Auth route can be accessed by our registered user only
# async def comment_create(
#     blog_id: uuid.UUID,
#     comment: CommentCreate, 
#     user_id = Depends(get_current_user), 
#     db: AsyncSession = Depends(get_db)
# ):
#     return await create_comment(blog_id, comment, user_id, db)


from sqlalchemy.ext.asyncio import AsyncSession
from blog.comments.schemas import CommentCreate, CommentUpdate, CommentResponse
from blog.comments.service import (
    create_comment, 
    get_comments_by_blog, 
    get_comment_by_id, 
    update_comment, 
    delete_comment,
    get_comment_replies
)
from db import get_db
from ..auth.middlewares import get_current_user

router = APIRouter()

@router.get("/blogs/{blog_id}/comments")
async def list_comments(
    blog_id: uuid.UUID, 
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List comments for a specific blog post with pagination."""
    return await get_comments_by_blog(blog_id, db, skip, limit)

@router.post("/blogs/{blog_id}/comments")
async def create_new_comment(
    blog_id: uuid.UUID,
    comment: CommentCreate, 
    current_user = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Create a new comment for a blog post."""
    return await create_comment(blog_id, comment, current_user, db)

@router.get("/comments/{comment_id}")
async def get_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a specific comment by its ID."""
    comment = await get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/comments/{comment_id}")
async def update_existing_comment(
    comment_id: uuid.UUID,
    comment_update: CommentUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing comment."""
    updated_comment = await update_comment(comment_id, comment_update, current_user, db)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found or you're not authorized to update it")
    return updated_comment

@router.delete("/comments/{comment_id}", status_code=204)
async def delete_existing_comment(
    comment_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an existing comment."""
    success = await delete_comment(comment_id, current_user, db)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or you're not authorized to delete it")

@router.get("/comments/{comment_id}/replies")
async def list_comment_replies(
    comment_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List replies to a specific comment with pagination."""
    return await get_comment_replies(comment_id, db, skip, limit)

@router.post("/comments/{comment_id}/replies")
async def create_comment_reply(
    comment_id: uuid.UUID,
    reply: CommentCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a reply to a specific comment."""
    parent_comment = await get_comment_by_id(comment_id, db)
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    reply.parent_id = comment_id
    return await create_comment(parent_comment.blog_id, reply, current_user, db)