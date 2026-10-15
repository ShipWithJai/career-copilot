import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.config import get_settings

settings = get_settings()

client=genai.Client(api_key=settings.GEMINI_API_KEY)

class Experience(BaseModel):
    company: str
    role: str
    duration: Optional[str] = Field(description="e.g., 'Jan 2020 - Present'")
    highlights: List[str] = Field(description="Bullet points of achievements")

class Education(BaseModel):
    institution: str
    degree: str
    graduation_year: Optional[str]

class Project(BaseModel):
    name:str
    description:str
    technologies_used:List[str]

class ParsedResume(BaseModel):
    skills: List[str]
    experience: List[Experience]
    education: List[Education]
    projects:List[Project]

async def parse_resume_text(raw_text: str) -> ParsedResume:
    prompt = f"""
    You are a precise data extractor. Extract the user's skills, experience, education, and projects from the provided resume text. 
    Strictly adhere to the provided schema. Do not invent, infer, or hallucinate any information not explicitly present in the text.
    
    Resume Text:
    {raw_text}
    """
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt, 
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ParsedResume
        )
    )
    
    parsed_data = ParsedResume.model_validate_json(response.text) # type:ignore
    return parsed_data
   

if __name__ == "__main__":
    import asyncio
    sample_text = """
        ALEX CHEN
        AI Full-Stack Engineer

        SKILLS
        Python, FastAPI, PostgreSQL, LangChain, Docker, Git, REST APIs

        EXPERIENCE
        Software Engineering Intern | TechNova Solutions | Jan 2023 - Aug 2023
        - Built a robust REST API using FastAPI and SQLAlchemy to handle user authentication.
        - Automated lead generation workflows using Python scripts, increasing outreach efficiency by 40%.
        - Designed and implemented a PostgreSQL database schema for storing relational data.

        EDUCATION
        Bachelor of Science in Computer Science
        State University, Graduated: 2024

        PROJECTS
        Career Copilot AI
        Built an automated job application system that parses resumes and generates tailored cover letters.
        Technologies used: FastAPI, LangGraph, PostgreSQL, Celery.
        """
    result = asyncio.run(parse_resume_text(sample_text))
    print(result.model_dump_json(indent=2))
    