from fastapi import APIRouter, Depends
from app.services.job_sources.adzuna import fetch_adzuna_jobs
from app.services.job_fetcher import ingest_jobs
from app.api.routes.deps import get_current_user
from app.models.user_resume import User


router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/fetch", response_model=dict)
async def fetch_and_store_jobs(
    role: str, 
    location:str|None=None, 
    current_user: User = Depends(get_current_user)
):
    fetched_jobs_data = await fetch_adzuna_jobs(role=role, location=location, results_limit=15)
    
    if not fetched_jobs_data:
        return {"message": "No jobs found to ingest."}
    
    await ingest_jobs(fetched_jobs_data)
    
    return {"message": f"Successfully fetched, vectorized, and saved {len(fetched_jobs_data)} jobs."}