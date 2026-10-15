import httpx
from typing import List, Dict, Any
from app.core.config import get_settings

settings = get_settings()

async def fetch_adzuna_jobs(role: str, location: str, results_limit: int = 10) -> List[Dict[str, Any]]:
    app_id = settings.ADZUNA_APP_ID
    app_key = settings.ADZUNA_APP_KEY
    country = "in"
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_limit,
        "what": role,
        "where": location,
        "content-type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url,params=params)
        
    data = response.json()
    results = data.get("results", [])
    
    standardized_jobs = []
    for job in results:
        standardized_jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "apply_url": job.get("redirect_url"),
            "source": "adzuna"
        })
    return standardized_jobs
   

if __name__ == "__main__":
    import asyncio
    async def run_test():
        print("fetching jobs from adzuna...")
        jobs=await fetch_adzuna_jobs(role="Ai engineer",location="Delhi",results_limit=2)
        import json
        print(json.dumps(jobs,indent=2))
        
    asyncio.run(run_test())
