from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel,ConfigDict
import io
import PyPDF2
from celery.result import AsyncResult
from fastapi import UploadFile, File, Form
from app.db.session import get_db
from app.models.user_resume import User, Resume
from app.models.job import Job
from app.api.routes.deps import get_current_user
from app.services.resume_parser import parse_resume_text
from app.core.celery_app import celery_app
from app.services.pdf_tasks import generate_pdf_task


class ResumeCreate(BaseModel):
    title: str
    content: str
    
class ResumeResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    parsed_data:dict|None=None
    
    model_config = ConfigDict(from_attributes=True)

class ResumeRequest(BaseModel):
    job_id: int | None = None
    base_resume: str | None = None
    job_description: str | None = None

router = APIRouter(prefix="/resumes", tags=["resumes"])

@router.post("/", response_model=ResumeResponse)
async def create_resume(
    resume_in: ResumeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_resume = Resume(title=resume_in.title, content=resume_in.content, user_id=current_user.id)
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    
    return new_resume
    
    


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    file_bytes = await file.read()
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    
    parsed_resume_obj=await parse_resume_text(extracted_text)
    parsed_dict=parsed_resume_obj.model_dump()
    new_resume = Resume(title=title, content=extracted_text, user_id=current_user.id,parsed_data=parsed_dict)
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
 
    
    return new_resume
    

@router.post("/generate")
async def trigger_pdf_generation(
    request: ResumeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.job_id is not None:
        job_result = await db.execute(select(Job).where(Job.id == request.job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        resume_result = await db.execute(
            select(Resume)
            .where(Resume.user_id == current_user.id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume = resume_result.scalar_one_or_none()
        if not resume:
            raise HTTPException(status_code=400, detail="No base resume found. Please upload one first.")

        base_resume = resume.content
        job_description = job.description
    elif request.base_resume and request.job_description:
        base_resume = request.base_resume
        job_description = request.job_description
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide a job_id or both base_resume and job_description.",
        )

    task = generate_pdf_task.delay(base_resume=base_resume, job_description=job_description)  # type: ignore
    return {"task_id": task.id}

@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    _: User = Depends(get_current_user),
):
    task_result = AsyncResult(task_id, app=celery_app)
  
    if task_result.state == "SUCCESS":
        result_data = task_result.result 
        return {
            "status": "completed", 
            "pdf_base64": result_data.get("pdf_base64")
        }
    
    elif task_result.state == "FAILURE":
        return {"status": "failed", "error": str(task_result.info)}
  
    return {"status": "processing"}

    
    
