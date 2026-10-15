import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def clear_jobs():
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE jobs RESTART IDENTITY CASCADE;"))
        await session.commit()
        print("Jobs table completely cleared!")

if __name__ == "__main__":
    asyncio.run(clear_jobs())