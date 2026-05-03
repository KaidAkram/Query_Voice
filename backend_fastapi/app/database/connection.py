"""
Database Connection — PostgreSQL via SQLAlchemy
=================================================
Provides async database session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# from app.core.config import settings

# TODO: Replace with settings.async_database_url
DATABASE_URL = "postgresql+asyncpg://queryvoice:queryvoice@localhost:5432/queryvoice_db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency injection for database sessions."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
