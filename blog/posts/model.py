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

class Posts(Base, CreatedUpdatedMixin):   #TODO:change tbl name to blogs
    __tablename__ = "posts"
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    author_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    image_url:Mapped[str] = mapped_column(sa.String, nullable=True)
    slug: Mapped[str] = mapped_column(sa.String, nullable=True)
    content: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    summary: Mapped[str] = mapped_column(sa.String, nullable=False)
    status: Mapped[SQLAlchemyEnum] = mapped_column(SQLAlchemyEnum(statusEnum), nullable=False, default=statusEnum.DRAFT)
    published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    author = relationship('User')
    likes = relationship("Post_Likes", back_populates="post")
    views = relationship("Post_Views", back_populates="post")

class Post_Views(Base):  #TODO:change tbl name to blog_views
    __tablename__ = 'posts_views'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    post_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    viewed_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    post = relationship("Posts", back_populates="views")

class Post_Likes(Base):  #TODO:change tbl name to blog_likes
    __tablename__ = 'posts_likes'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    post_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    liked_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    post = relationship("Posts", back_populates="likes")
