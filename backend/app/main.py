from fastapi import FastAPI
from app.api.routes import users,auth,resumes,jobs,search,customizer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Career Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(search.router)
app.include_router(customizer.router)

@app.get("/")
async def root():
    return {"message": "Career Copilot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True, port=8000)