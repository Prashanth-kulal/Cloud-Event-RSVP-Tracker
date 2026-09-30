"""
Async SQLAlchemy database engine and session factory for SQLite (local dev).
Cloud-ready: swap DATABASE_URL for PostgreSQL or use Firestore abstraction layer.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings

logger = logging.getLogger("database")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables on startup."""
    from backend.models import user, event, rsvp, waitlist, announcement, notification  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")


async def get_db():
    """FastAPI dependency — yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("Database session error: %s", exc)
            raise
        finally:
            await session.close()
