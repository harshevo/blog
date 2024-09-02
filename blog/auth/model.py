import uuid
import enum
import sqlalchemy as sa
from sqlalchemy import Enum as SQLAlchemyEnum, func, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class PowerRole(enum.Enum):
    USER = "user"
    AUTHOR = "author"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=func.uuid_generate_v4())
    fullname: Mapped[str] = mapped_column(sa.String, nullable=False)
    username: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String, unique=True, nullable = False) 
    password_hash: Mapped[str] = mapped_column(sa.String, unique = True, nullable = False)
    profile_picture_url: Mapped[str] = mapped_column(sa.String, nullable=True)
    bio_txt: Mapped[str] = mapped_column(sa.String, nullable=True)
    role: Mapped[SQLAlchemyEnum] = mapped_column(SQLAlchemyEnum(PowerRole), nullable=False, default=PowerRole.USER)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False) 
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    refresh_tokens = relationship('RefreshToken', back_populates='user')

class RefreshToken(Base):
    __tablename__='refresh_tokens'
    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key = True, server_default=func.uuid_generate_v4())
    token: Mapped[str] = mapped_column(sa.String, nullable = False, unique = True)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False) 
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship('User', back_populates='refresh_tokens')
    
