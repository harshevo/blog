import uuid
from db.base import Base
import sqlalchemy as sa
from sqlalchemy import func, DateTime 
from sqlalchemy import ForeignKey
from  sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class BlogLikes(Base):  #TODO:change tbl name to blog_likes
    __tablename__ = 'blog_likes'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    blog_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('blogs.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    liked_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    blog = relationship("Blog", back_populates="likes")
