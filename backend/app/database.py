"""
Database Connection and Session Management
Async SQLAlchemy with aiosqlite/asyncpg
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Convert sync URLs to async URLs
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
# postgresql+asyncpg:// is already async-ready

# Create async engine with appropriate settings
engine_kwargs = {
    "echo": False,
}
# SQLite needs special handling for async
if "sqlite" in database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(database_url, **engine_kwargs)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get async DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered with Base
    from app.models import booking, branch, chat, customer, menu, order, preference, staff, table
    # Import domain models
    from app.domains.checkin import models as checkin_models
    from app.domains.kitchen import events as kitchen_events

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
