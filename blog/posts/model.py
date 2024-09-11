import uuid
import enum
import sqlalchemy as sa
from sqlalchemy import JSON, Null, false, func, DateTime, Enum as SQLAlchemyEnum, null
from sqlalchemy import ForeignKey
from sqlalchemy.exc import DataError
from  sqlalchemy.orm import Mapped, backref, mapped_column, relationship
from db.base import Base, CreatedUpdatedMixin
from ..auth.model import User

class statusEnum(enum.Enum):
    DRAFT="draft"
    PUBLISHED="published"
    PRIVATE="private"

    #TODO: Create New table for image

class Blog(Base, CreatedUpdatedMixin):   #TODO:change tbl name to blogs
    __tablename__ = "blogs"
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    author_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    slug: Mapped[str] = mapped_column(sa.String, nullable=True)
    content: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    summary: Mapped[str] = mapped_column(sa.String, nullable=False)
    status: Mapped[SQLAlchemyEnum] = mapped_column(SQLAlchemyEnum(statusEnum), nullable=False, default=statusEnum.DRAFT)
    published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    author = relationship('User')
    likes = relationship("BlogLikes", back_populates="blog")
    views = relationship("BlogViews", back_populates="blog")
    images = relationship("BlogImage", back_populates="blog")
    # tags = relationship("BlogTag", back_populates="blog")
    tags = relationship("BlogTag", back_populates="blog", cascade="all, delete-orphan")
    categories = relationship("BlogCategory", back_populates="blog")


class BlogImage(Base):
    __tablename__ = 'blog_images'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    blog_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('blogs.id', ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(sa.String, nullable=False)
    blog = relationship("Blog", back_populates="images")


class BlogViews(Base):  #TODO:change tbl name to blog_views
    __tablename__ = 'blog_views'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    blog_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('blogs.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    viewed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    blog = relationship("Blog", back_populates="views")

