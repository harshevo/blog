import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import AsyncSession
from typing import List
from . import schemas
from . import service as service
from db import get_db
from fastapi import Depends
from blog.auth.middlewares import get_current_user, get_current_super_admin
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

# Category routes
@router.post("/categories/", status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Allows users to create new categories for organizing blog posts
    - Used in the blog management section when setting up or managing categories
    """
    return await service.create_category(db, category, current_user)

@router.get("/categories/")
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    - Retrieves a list of all categories
    - Used in category selection dropdowns, sidebars, or category pages
    """
    return await service.get_categories(db, skip=skip, limit=limit)

@router.get("/categories/{category_id}", response_model=schemas.Category)
async def get_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    - Retrieves details of a specific category
    - Used when displaying category information or editing a category
    """
    db_category = await service.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: uuid.UUID,
    category: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    - Allows users to update their own categories
    - Used in the category management section to edit category details
    """
    db_category =  await service.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.user_id != uuid.UUID(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to update this category")
    return  await service.update_category(db, category_id, category, uuid.UUID(current_user))

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user  = Depends(get_current_user)
):
    """
    - Allows users to delete their own categories
    - Used in the category management section to remove unwanted categories
    """
    db_category =  await service.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.user_id != uuid.UUID(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this category")
    await service.delete_category(db, category_id, uuid.UUID(current_user))

# Super admin routes
@router.get("/admin/categories/", response_model=List[schemas.CategoryWithUserID])
async def list_all_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_super_admin)
):
    """
    - Allows super admins to view all categories with user information
    - Used in the admin panel for monitoring and managing all categories
    """
    return  await service.get_all_categories(db, skip=skip, limit=limit)

@router.put("/admin/categories/{category_id}", response_model=schemas.Category)
async def admin_update_category(
    category_id: uuid.UUID,
    category: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin  = Depends(get_current_super_admin)
):
    """
    - Allows super admins to update any category
    - Used in the admin panel to manage and moderate categories
    """
    db_category =  await service.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return  await service.update_category(db, category_id, category, uuid.UUID(current_admin))

@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_super_admin)
):
    """
    - Allows super admins to delete any category
    - Used in the admin panel to remove inappropriate or obsolete categories
    """
    if not  await service.delete_category(db, category_id, uuid.UUID(current_admin)):
        raise HTTPException(status_code=404, detail="Category not found")

# Tag routes
@router.post("/tags/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: schemas.TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Allows users to create new tags for labeling blog posts
    - Used when writing or editing blog posts to add new tags
    """
    return  await service.create_tag(db, tag, current_user)

@router.get("/tags/", response_model=List[schemas.Tag])
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    - Retrieves a list of all tags
    - Used in tag clouds, search functionalities, or tag selection interfaces
    """
    return  await service.get_tags(db, skip=skip, limit=limit)

@router.get("/tags/{tag_id}", response_model=schemas.Tag)
async def get_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    - Retrieves details of a specific tag
    - Used when displaying tag information or editing a tag
    """
    db_tag =  await service.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.put("/tags/{tag_id}", response_model=schemas.Tag)
async def update_tag(
    tag_id: uuid.UUID,
    tag: schemas.TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Allows users to update their own tags
    - Used in the tag management section to edit tag details
    """
    db_tag =  await service.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    if db_tag.user_id != uuid.UUID(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to update this tag")
    return  await service.update_tag(db, tag_id, tag, uuid.UUID(current_user))

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Allows users to delete their own tags
    - Used in the tag management section to remove unwanted tags
    """
    db_tag =  await service.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    if db_tag.user_id != uuid.UUID(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this tag")
    await service.delete_tag(db, tag_id, uuid.UUID(current_user))

# Post-related routes
@router.post("/blogs/{blog_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_category_to_blog(
    blog_id: uuid.UUID,
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Assigns a category to a specific blog post
    - Used when creating or editing a blog post to categorize it
    """
    return await service.add_category_to_blog(db, blog_id, category_id, current_user)

@router.delete("/blogs/{blog_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category_from_blog(
    blog_id: uuid.UUID,
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Removes a category from a specific blog post
    - Used when editing a blog post to change its categorization
    """
    if not  await service.remove_category_from_blog(db, blog_id, category_id, current_user):
        raise HTTPException(status_code=404, detail="Blog or Category not found or not authorized")

@router.post("/blogs/{blog_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_blog(
    blog_id: uuid.UUID,
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Adds a tag to a specific blog post
    - Used when creating or editing a blog post to add relevant tags
    """
    if not  await service.add_tag_to_blog(db, blog_id, tag_id, current_user):
        raise HTTPException(status_code=404, detail="Blog or Tag not found or not authorized")

@router.delete("/blogs/{blog_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_blog(
    blog_id: uuid.UUID,
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user= Depends(get_current_user)
):
    """
    - Removes a tag from a specific blog post
    - Used when editing a blog post to update its tags
    """
    if not await service.remove_tag_from_blog(db, blog_id, tag_id, current_user):
        raise HTTPException(status_code=404, detail="Blog or Tag not found or not authorized")

@router.get("/blogs/{blog_id}/categories")
async def get_blog_categories(blog_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    - Retrieves all categories associated with a specific blog post
    - Used when displaying a blog post to show its categories
    """
    return  await service.get_blog_categories(db, blog_id)

@router.get("/blogs/{blog_id}/tags", response_model=List[schemas.Tag])
async def get_blog_tags(blog_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    - Retrieves all tags associated with a specific blog post
    - Used when displaying a blog post to show its tags
    """
    return  await service.get_blog_tags(db, blog_id)


