import asyncio
from pydantic import BaseModel
from google import genai
from google.genai import types
from fpdf import FPDF
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class TailoredRole(BaseModel):
    job_title: str
    company: str
    dates: str
    bullets: list[str]

class TailoredResume(BaseModel):
    name: str
    contact_info: str
    professional_summary: str
    skills: list[str]
    experience: list[TailoredRole]

async def generate_tailored_resume_data(base_resume: str, job_description: str) -> TailoredResume:
    prompt = f"""
    You are an expert executive recruiter specializing in career pivots. Tailor the base resume to the target job.
    
    CRITICAL RULES:
    1. Truthfulness: Do not invent or exaggerate experience.
    2. Transferable Skills: Explicitly reframe the existing experience to highlight transferable skills.
    
    STRICT LENGTH CONSTRAINTS:
    - Professional Summary: Exactly 3 to 4 sentences long.
    - Skills: Exactly 15 to 20 comma-separated skills.
    - Experience: Keep the original job titles, companies, and dates from the Base Resume. Write exactly 2 to 3 tailored bullets per role. Each bullet must be between 20 and 30 words.
    
    Base Resume:
    {base_resume}
    
    Target Job Description:
    {job_description}
    """
    
    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TailoredResume,
        )
    )
    return TailoredResume.model_validate_json(response.text) # type: ignore

def create_pdf(resume_data: TailoredResume) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(w=0, h=10, text=resume_data.name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(w=0, h=6, text=resume_data.contact_info, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(w=0, h=6, text="SUMMARY", new_x="LMARGIN", new_y="NEXT")
    current_y = pdf.get_y()
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(w=0, h=5, text=resume_data.professional_summary, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(w=0, h=6, text="EXPERIENCE", new_x="LMARGIN", new_y="NEXT")
    current_y = pdf.get_y()
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(2)
    
    for role in resume_data.experience:
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(w=130, h=6, text=f"{role.job_title} | {role.company}")
        
        pdf.set_font("helvetica", "", 10)
        pdf.cell(w=0, h=6, text=role.dates, align="R", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        for bullet in role.bullets:
            clean_bullet = bullet.replace("'", "'").replace('"', '"').replace("–", "-").encode('latin-1', 'replace').decode('latin-1')
            pdf.set_x(20) 
            pdf.multi_cell(w=0, h=5, text=f"- {clean_bullet}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(w=0, h=6, text="SKILLS", new_x="LMARGIN", new_y="NEXT")
    current_y = pdf.get_y()
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 10)
    skills_text = ", ".join(resume_data.skills)
    pdf.multi_cell(w=0, h=5, text=skills_text, new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

if __name__ == "__main__":
    async def test():
        base = """
        Alex Chen
        alex@example.com
        Experience:
        Data Analyst | Tech Corp | Jan 2020 - Present
        - Analyzed 10k rows of SQL data.
        - Built dashboards.
        """
        jd = "Looking for a Data Scientist with SQL and dashboarding experience."
        
        data = await generate_tailored_resume_data(base, jd)
        pdf_bytes = create_pdf(data)
        
        with open("test_nested_resume.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Test passed: test_nested_resume.pdf created.")
        
    asyncio.run(test())