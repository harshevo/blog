import uuid
import sqlalchemy as sa 
from sqlalchemy import Column, Date, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.orm import backref
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
    # replies = relationship("Comment", backref="parent", cascade="all, delete", remote_side=[id]) 
    replies = relationship("Comment", backref=backref("parent", remote_side=[id]), cascade="all, delete")

    # Optional relationships to User and Blog models
    user = relationship("User", backref="comments")
    blog = relationship("Blog", backref="comments")

# The structure you've created for the Comment model is generally a good approach for a blog application. Let's review the key aspects and suggest a minor improvement:
# The basic fields (id, content, created_at, updated_at) are well-defined.
# Foreign key relationships to blogs and users are correctly established.
# The self-referential relationship for nested comments (replies) is implemented.
# One small improvement we can make is to the replies relationship. Here's the updated version:
# This change clarifies the remote_side usage. The remote_side=[id] is used in the backref to indicate that the id column is on the "remote" side of the relationship when accessed via the parent attribute.
# Explanation of remote_side:
# In a self-referential relationship, SQLAlchemy needs to know which side is the "parent" and which is the "child".
# remote_side=[id] tells SQLAlchemy that the id column is on the "many" side of the one-to-many relationship.
# This allows you to access a comment's replies via comment.replies and a reply's parent via reply.parent.
# The rest of your model looks good and appropriate for a blog comment system. It allows for:
# Associating comments with users and blog posts
# Nested comments (replies to comments)
# Proper cascading deletions
# Timestamp tracking
# This structure should work well for most blog comment implementations.