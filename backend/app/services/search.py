from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.job import Job
from app.services.embeddings import get_embedding

async def search_jobs(user_query: str, location_filter: str | None = None, limit: int = 5):
    """Embeds a user query and finds the most semantically similar jobs, with optional geographic filtering."""
    query_vector = await get_embedding(user_query)
    
    async with AsyncSessionLocal() as session:
        stmt = select(Job)
        
        if location_filter:
            stmt = stmt.where(Job.location.ilike(f"%{location_filter}%"))
            
        stmt = stmt.order_by(Job.embeddings.cosine_distance(query_vector)).limit(limit)
        
        result = await session.execute(stmt)
        return result.scalars().all()  

if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        print("Searching for: 'Entry level Python AI role'")
        matches = await search_jobs("Ai engineers, in delhi")
        for job in matches:
            print(f"- {job.title} at {job.company}")
        
    asyncio.run(run_test())