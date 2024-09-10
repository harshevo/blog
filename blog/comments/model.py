import uuid
import sqlalchemy as sa 
from sqlalchemy import Column, Date, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base

# This Model is made by Chat-GPT 
class Comment(Base):
    __tablename__ = "comments"

    id:Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    content:Mapped[str] = mapped_column(sa.String, nullable=False)
    created_at:Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at:Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Foreign key references
    blog_id:Mapped[uuid.UUID] =mapped_column(sa.UUID, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id:Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id:Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    """
      I don't fully understand { remote_side=[id] }
      I got some points on this Link, If you want to refer to
      https://stackoverflow.com/questions/45221443/how-to-better-understand-remote-side-in-sqlalchemy 
    """
    replies = relationship("Comment", backref="parent", cascade="all, delete", remote_side=[id]) 

    # Optional relationships to User and Blog models
    user = relationship("User", backref="comments")
    blog = relationship("Blog", backref="comments")

