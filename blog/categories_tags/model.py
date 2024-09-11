import uuid
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
import sqlalchemy as sa

class BlogTag(Base):
    __tablename__ = "blog_tags"

    blog_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    blog = relationship("Blog", back_populates="tags")
    tag = relationship("Tag", back_populates="blog_tags")

    __table_args__ = (
        UniqueConstraint('blog_id', 'tag_id', name='uq_blog_tag'),
        Index('idx_blog_tag', 'blog_id', 'tag_id'),
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    blog_tags = relationship("BlogTag", back_populates="tag", cascade="all, delete-orphan")
    user = relationship("User", back_populates="tags")

    __table_args__ = (
        UniqueConstraint('name', name='uq_tag_name'),
        UniqueConstraint('slug', name='uq_tag_slug'),
        Index('idx_tag_created_at', 'created_at'),
    )



class BlogCategory(Base):
    __tablename__ = "blog_categories"

    blog_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    blog = relationship("Blog", back_populates="categories")
    category = relationship("Category", back_populates="blogs")

    __table_args__ = (
        UniqueConstraint('blog_id', 'category_id', name='uq_blog_category'),
        Index('idx_blog_category', 'blog_id', 'category_id'),
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    blogs = relationship("BlogCategory", back_populates="category", cascade="all, delete-orphan")
    user = relationship("User", back_populates="categories")
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_category_name'),
        UniqueConstraint('slug', name='uq_category_slug'),
        Index('idx_category_created_at', 'created_at'),
    )