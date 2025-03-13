from typing import AsyncGenerator, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.db,
    echo=True  # Set to False in production
)

# Async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    #Relation to todos
    todos: List["Todo"] = Relationship(back_populates="user")

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task: str
    completed: bool = False
    user_id: int = Field(
        default=None,
        foreign_key="user.id",
        index=True  #Faster querying by user_id
    )

    user: Optional[User] = Relationship(back_populates="todos")

async def create_db_and_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def close_engine():
    try:
        await engine.dispose()
        logger.info("Database engine closed successfully.")
    except Exception as e:
        logger.error(f"Error closing database engine: {e}")
    finally:
        if 'sqlite' in str(engine.url):
            await engine.dispose()