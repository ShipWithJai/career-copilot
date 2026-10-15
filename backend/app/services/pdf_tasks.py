import asyncio
import base64
from app.core.celery_app import celery_app
from app.services.customizer import generate_tailored_resume_data, create_pdf

@celery_app.task(bind=True, name="app.services.pdf_tasks.generate_pdf_task")
def generate_pdf_task(self, base_resume: str, job_description: str):
    
    resume_data = asyncio.run(
        generate_tailored_resume_data(base_resume, job_description)
    )
    
    pdf_bytes = create_pdf(resume_data)
    
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return {"status": "completed", "pdf_base64": pdf_base64}

if __name__ == "__main__":
    print("Starting local test...")
    dummy_resume = "Software Engineer with 3 years of Python experience."
    dummy_job = "Looking for a backend developer skilled in Python and APIs."
    
    test_result = generate_pdf_task(base_resume=dummy_resume,job_description=dummy_job) #type:ignore
    
    print("\n--- Task Result ---")
    print(f"Status: {test_result['status']}")
    print(f"Base64 Output (first 100 chars): {test_result['pdf_base64'][:100]}...")