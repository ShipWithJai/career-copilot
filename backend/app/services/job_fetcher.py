import asyncio,json
from app.db.session import AsyncSessionLocal
from app.models.job import Job
from app.services.embeddings import get_embedding
from app.services.job_sources.adzuna import fetch_adzuna_jobs
from app.core.celery_app import celery_app


async def ingest_jobs(raw_jobs: list[dict]):
    """Iterates through fetched jobs, generates vector embeddings, and persists them."""
    async with AsyncSessionLocal() as session:
        for job_data in raw_jobs:
            content = f"Title: {job_data['title']}\nCompany: {job_data.get('company', '')}\nLocation: {job_data.get('location', '')}\nDescription: {job_data.get('description', '')}"

            vector = await get_embedding(content)
            
            # Ensure the vector is a Python list of floats, not a string
            if isinstance(vector, str):
                vector = json.loads(vector)
            
            new_job = Job(
                title=job_data.get("title", "No Title"),
                company=job_data.get("company", "Unknown"), 
                location=job_data.get("location", "Unknown"), 
                description=job_data.get("description", ""),
                apply_url=job_data.get("apply_url", "https://example.com"),
                source=job_data.get("source", "Adzuna"),
                embeddings=vector  
            )
            
            session.add(new_job)

            await asyncio.sleep(0.5)

        await session.commit()

        print("Successfully ingested and vectorized jobs batch.")
        
        
async def fetch_and_ingest():
    target_searches = [
        {"role": "AI Engineer", "location": "Delhi"},
        {"role": "Data Scientist", "location": "Bangalore"},
        {"role": "Backend Developer", "location": "Remote"},
        {"role": "Machine Learning", "location": "Mumbai"}
    ]
    
    for search in target_searches:
        print(f"Fetching {search['role']} roles in {search['location']}...")
        
        batch = await fetch_adzuna_jobs(
            role=search["role"], 
            location=search["location"], 
            results_limit=20
        )
        
        if batch:
            await ingest_jobs(batch)
            
        # Pause for 2 seconds before the next API call to prevent rate-limit bans
        await asyncio.sleep(2) 

@celery_app.task(name="app.services.job_fetcher.scheduled_job_fetch")
def scheduled_job_fetch():
    asyncio.run(fetch_and_ingest())  
if __name__ == "__main__":
    test_batch=asyncio.run(fetch_adzuna_jobs(role="Ai engineer",location="Delhi",results_limit=2))
    asyncio.run(ingest_jobs(test_batch))