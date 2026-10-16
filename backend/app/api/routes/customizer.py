from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.routes.deps import get_current_user
from app.db.session import get_db
from app.models.job import Job
from app.models.user_resume import User, Resume
from app.services.customizer import (
    ResumeValidationError,
    create_pdf,
    generate_tailored_resume_data,
)

router = APIRouter(prefix="/customizer", tags=["customizer"])

@router.post("/{job_id}", response_class=Response)
async def customize_resume_for_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates a customized PDF resume for a specific job."""
    
    stmt_job = select(Job).where(Job.id == job_id)
    result_job = await db.execute(stmt_job)
    job = result_job.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    stmt_resume = select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).limit(1)
    result_resume = await db.execute(stmt_resume)
    base_resume = result_resume.scalar_one_or_none()
    
    if not base_resume:
        raise HTTPException(status_code=400, detail="No base resume found. Please upload one first.")
        
    try:
        tailored_data = await generate_tailored_resume_data(
            base_resume=base_resume.content,
            job_description=job.description,
        )
    except ResumeValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="The generated resume did not pass validation. Please try again.",
        ) from exc
    
    pdf_bytes = create_pdf(tailored_data)
    
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=resume_job_{job_id}.pdf"}
    )