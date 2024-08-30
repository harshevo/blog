import json
from typing import AsyncGenerator

import pydantic.json
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .base import Base


def _custom_json_serializer(*args, **kwargs) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs)


# isort: off
# A quirk of SQLAlchemy is that all models must be imported after the Base class
# and before the Session class is created for cross module relationships to work.
# We collect all the models in the adjacent models.py file and import them here.
from . import models  # type: ignore

# https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.params.echo
# echo: str | bool
# if settings.DEBUG:
#     echo = "debug"
# else:
#     echo = False

engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5435/postgres", echo=True, json_serializer=_custom_json_serializer)
Session = async_sessionmaker(engine, expire_on_commit=False)


# https://docs.python.org/3/library/typing.html#typing.AsyncGenerator
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator function to yield a new database session.

    This function yields a new database session wrapped inside an asynchronous
    context manager. The session will automatically be committed/rolled back
    when the context is exited.
    """
    async with Session() as session:
        yield session
