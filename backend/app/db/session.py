import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    """Yields a database session and automatically closes it after the request."""
    async with AsyncSessionLocal() as session:
        yield session

if __name__ == "__main__":
    async def test_connection():
        try:
            async with engine.begin() as conn:
                print("Database connection successful!")
        except Exception as e:
            print(f"Database connection failed: {e}")
        finally:
            await engine.dispose()

    asyncio.run(test_connection())