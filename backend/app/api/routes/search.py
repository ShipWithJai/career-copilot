from fastapi import APIRouter, HTTPException, Query,Depends
from pydantic import BaseModel
from app.services.search import search_jobs
from app.api.routes.deps import get_current_user

router = APIRouter()
class JobSearchResult(BaseModel):
    id: int
    title: str
    company: str
    location: str
    apply_url: str

    class Config:
        # This tells Pydantic to read data from SQLAlchemy objects, not just dictionaries
        from_attributes = True 

@router.get("/semantic", response_model=list[JobSearchResult])
async def search_jobs_api(
    q: str = Query(..., min_length=3, description="The job search query (e.g., 'AI Engineer')"),
    location: str | None = Query(None, description="Optional city or state filter"),
    limit: int = Query(5, ge=1, le=20),
    current_user=Depends(get_current_user),
):
    """Executes a hybrid search: semantic vector matching + strict location filtering."""
    
    matches = await search_jobs(user_query=q, location_filter=location, limit=limit)
    
    if not matches:
       raise HTTPException(status_code=404, detail="No matching jobs found in that location") 
   
    return matches