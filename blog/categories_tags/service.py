import uuid
from fastapi import HTTPException, status
from blog.posts import model as blog_model
from sqlalchemy import select, exists, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from blog.categories_tags import model as models
from blog.categories_tags import schemas as schemas




async def create_category(db: AsyncSession, category: schemas.CategoryCreate, user_id: uuid.UUID):
    existing_category = await db.execute(
        select(exists().where(
            or_(
                models.Category.name == category.name,
                models.Category.slug == category.slug
            )
        )
    )
    )
    if existing_category.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name or slug already exists"
        )
    db_category = models.Category(**category.dict(), user_id=user_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(models.Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_category(db: AsyncSession, category_id: uuid.UUID):
    stmt = select(models.Category).where(models.Category.id == category_id)
    result = await db.execute(stmt)
    return result.scalar()


async def update_category(db: AsyncSession, category_id: uuid.UUID, category: schemas.CategoryUpdate, user_id: uuid.UUID):
    category_stmt_exec = await db.execute(
            select(models.Category).
            where(models.Category.id == category_id))
    db_category = category_stmt_exec.scalar_one_or_none()

    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if db_category.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this category")
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category(db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID):
    category_stmt_exec = await db.execute(
                select(models.Category)
                .where(models.Category.id == category_id)
            )
    db_category = category_stmt_exec.scalar_one_or_none()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if db_category.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this category")
    await db.delete(db_category)
    await db.commit()
    return True


async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    category_stmt= (
            select(models.Category)
            .limit(limit)
            .offset(skip)
            )
    result = await db.execute(category_stmt)
    categories = result.scalars().all()
    return categories


async def admin_update_category(db: AsyncSession, category_id: uuid.UUID, category: schemas.CategoryUpdate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def admin_delete_category(db: AsyncSession, category_id: uuid.UUID):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await db.delete(db_category)
    await db.commit()
    return True


async def create_tag(db: AsyncSession, tag: schemas.TagCreate, user_id: uuid.UUID):
    existing_tag = await db.execute(
        select(exists().where(
            or_(
                models.Tag.name == tag.name,
                models.Tag.slug == tag.slug
            )
        )
    )
    )
    if existing_tag.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name or slug already exists"
        )
    db_tag = models.Tag(**tag.dict(), user_id=user_id)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(models.Tag).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_tag(db: AsyncSession, tag_id: uuid.UUID):
    stmt = select(models.Tag).where(models.Tag.id == tag_id)
    result = await db.execute(stmt)
    return result.scalar()


async def update_tag(db: AsyncSession, tag_id: uuid.UUID, tag: schemas.TagUpdate, user_id: uuid.UUID):
    stmt_tag = await db.execute(
                select(models.Tag)
                .where(models.Tag.id == tag_id)
            )
    db_tag = stmt_tag.scalars().first()
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if db_tag.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this tag")
    for key, value in tag.dict(exclude_unset=True).items():
        setattr(db_tag, key, value)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


async def delete_tag(db: AsyncSession, tag_id: uuid.UUID, user_id: uuid.UUID):
    stmt_tag = await db.execute(
                select(models.Tag)
                .where(models.Tag.id == tag_id)
            )
    db_tag = stmt_tag.scalars().first()
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if db_tag.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tag")
    await db.delete(db_tag)
    await db.commit()
    return True


async def _check_blog_access_and_category_exists(db: AsyncSession, blog_id: uuid.UUID, category_id: uuid.UUID, user_id: uuid.UUID):
    stmt = select(
        exists().where(and_(blog_model.Blog.id == blog_id, blog_model.Blog.author_id == user_id)).label('blog_access'),
        exists().where(models.Category.id == category_id).label('category_exists')
    )
    result = await db.execute(stmt)
    row = result.first()
    return row.blog_access, row.category_exists


async def add_category_to_blog(db: AsyncSession, blog_id: uuid.UUID, category_id: uuid.UUID, user_id: uuid.UUID):
    blog_access, category_exists = await _check_blog_access_and_category_exists(db, blog_id, category_id, user_id)
    
    if not blog_access:
        raise HTTPException(status_code=404, detail="Blog not found or not authorized")
    
    if not category_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    stmt = select(exists().where(models.BlogCategory.blog_id == blog_id, models.BlogCategory.category_id == category_id))
    if await db.scalar(stmt):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already added to this blog")
    
    data = models.BlogCategory(blog_id=blog_id, category_id=category_id)
    db.add(data)
    await db.commit()
    return True


async def remove_category_from_blog(db: AsyncSession, blog_id: uuid.UUID, category_id: uuid.UUID, user_id: uuid.UUID):
    blog_access, category_exists = await _check_blog_access_and_category_exists(db, blog_id, category_id, user_id)
    
    if not blog_access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or not authorized")
    
    if not category_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    stmt = select(models.BlogCategory).where(models.BlogCategory.blog_id == blog_id, models.BlogCategory.category_id == category_id)
    result = await db.execute(stmt)
    blog_category = result.scalar_one_or_none()
    if blog_category:
        await db.delete(blog_category)
        await db.commit()
        return True
    return False


async def _check_blog_access_and_tag_exists(db: AsyncSession, blog_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID):
    stmt = select(
        exists().where(and_(blog_model.Blog.id == blog_id, blog_model.Blog.author_id == user_id)).label('blog_access'),
        exists().where(models.Tag.id == tag_id).label('tag_exists')
    )
    result = await db.execute(stmt)
    row = result.first()
    return row.blog_access, row.tag_exists


async def add_tag_to_blog(db: AsyncSession, blog_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID):
    blog_access, tag_exists = await _check_blog_access_and_tag_exists(db, blog_id, tag_id, user_id)
    
    if not blog_access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or not authorized")
    
    if not tag_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    stmt = select(exists().where(models.BlogTag.blog_id == blog_id, models.BlogTag.tag_id == tag_id))
    if await db.scalar(stmt):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already added to this blog")
    
    blog_tag = models.BlogTag(blog_id=blog_id, tag_id=tag_id)
    db.add(blog_tag)
    await db.commit()
    
    return True


async def remove_tag_from_blog(db: AsyncSession, blog_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID):
    blog_access, tag_exists = await _check_blog_access_and_tag_exists(db, blog_id, tag_id, user_id)
    
    if not blog_access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or not authorized")
    
    if not tag_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    stmt = select(models.BlogTag).where(models.BlogTag.blog_id == blog_id, models.BlogTag.tag_id == tag_id)
    result = await db.execute(stmt)
    blog_tag = result.scalar_one_or_none()
    if blog_tag:
        await db.delete(blog_tag)
        await db.commit()
        return True
    return False
    

async def get_blog_categories(db: AsyncSession, blog_id: uuid.UUID):
    stmt = (
        select(models.Category)
        .join(models.BlogCategory, models.Category.id == models.BlogCategory.category_id)
        .where(models.BlogCategory.blog_id == blog_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_blog_tags(db: AsyncSession, blog_id: uuid.UUID):
    stmt = (
        select(models.Tag)
        .join(models.BlogTag, models.Tag.id == models.BlogTag.tag_id)
        .where(models.BlogTag.blog_id == blog_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
