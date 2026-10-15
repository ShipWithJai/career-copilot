from fpdf import FPDF
from pydantic import BaseModel

class TailoredResume(BaseModel):
    name: str
    contact_info: str
    professional_summary: str
    skills: list[str]
    experience_bullets: list[str]

def create_pdf(resume_data: TailoredResume) -> bytes:
    """Takes structured resume data and renders it into a professionally formatted PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    BODY_SIZE = 11
    HEADER_SIZE = 24
    SECTION_TITLE_SIZE = 14
    SUB_TITLE_SIZE = 12
    LINE_HEIGHT = 6
    SECTION_SPACING = 8
    
    pdf.set_font("helvetica", "B", HEADER_SIZE)
    pdf.cell(w=0, h=12, text=resume_data.name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", BODY_SIZE)
    pdf.cell(w=0, h=6, text=resume_data.contact_info, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(SECTION_SPACING)
    
    pdf.set_font("helvetica", "B", SECTION_TITLE_SIZE)
    pdf.cell(w=0, h=6, text="SUMMARY", new_x="LMARGIN", new_y="NEXT")
    
    current_y = pdf.get_y() + 2
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(4)
    
    pdf.set_font("helvetica", "", BODY_SIZE)
    pdf.multi_cell(w=0, h=LINE_HEIGHT, text=resume_data.professional_summary, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(SECTION_SPACING)
    
    pdf.set_font("helvetica", "B", SECTION_TITLE_SIZE)
    pdf.cell(w=0, h=6, text="EXPERIENCE", new_x="LMARGIN", new_y="NEXT")
    
    current_y = pdf.get_y() + 2
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(4)
    
    pdf.set_font("helvetica", "B", SUB_TITLE_SIZE)
    pdf.cell(w=100, h=LINE_HEIGHT, text="Target Role Experience")
    pdf.set_font("helvetica", "", BODY_SIZE)
    pdf.cell(w=0, h=LINE_HEIGHT, text="Recent - Present", align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", BODY_SIZE)
    for bullet in resume_data.experience_bullets:
        clean_bullet = bullet.replace("'", "'").replace('"', '"').replace("–", "-").encode('latin-1', 'replace').decode('latin-1')
        pdf.set_x(20)
        pdf.multi_cell(w=0, h=LINE_HEIGHT, text=f"- {clean_bullet}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(SECTION_SPACING)
    
    pdf.set_font("helvetica", "B", SECTION_TITLE_SIZE)
    pdf.cell(w=0, h=6, text="SKILLS", new_x="LMARGIN", new_y="NEXT")
    
    current_y = pdf.get_y() + 2
    pdf.line(x1=pdf.l_margin, y1=current_y, x2=pdf.w - pdf.r_margin, y2=current_y)
    pdf.ln(4)
    
    pdf.set_font("helvetica", "", BODY_SIZE)
    skills_text = ", ".join(resume_data.skills)
    pdf.multi_cell(w=0, h=LINE_HEIGHT, text=skills_text, new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

if __name__ == "__main__":
    def test_layout():
        mock_data = TailoredResume(
            name="Alex Morgan",
            contact_info="alex.morgan@example.com | +00 00000 00000 | Springfield, Country | github.com/alexmorgan-sample",
            professional_summary="Software engineer with 8+ years of experience building scalable web services and data pipelines. Strong in backend architecture, cloud infrastructure, and mentoring teams. Passionate about clean code, reliable systems, and shipping products users love. Consistently recognized for delivering high-impact solutions that drive revenue growth and operational efficiency.",
            skills=["Python", "JavaScript/TypeScript", "Java", "SQL", "Bash", "Django", "FastAPI", "Node.js", "React", "GraphQL", "AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Prometheus", "PostgreSQL", "Redis", "Kafka", "Airflow"],
            experience_bullets=[
                "Led a team of 5 engineers to redesign the order-processing platform, cutting average latency by 42% and increasing throughput by 150% during peak holiday traffic.",
                "Migrated 30+ microservices to Kubernetes, improving deployment frequency from weekly to daily and reducing infrastructure costs by 20%.",
                "Introduced automated testing and observability standards using Prometheus and Grafana, reducing production incidents by 35% and accelerating mean time to recovery (MTTR).",
                "Mentored 4 junior developers; two were promoted within 18 months after successfully delivering mission-critical API integrations.",
                "Designed and implemented an ETL pipeline processing 10 GB of daily data, saving the analytics team 15 hours a week in manual data aggregation.",
                "Collaborated closely with product and design teams to launch a customer-facing analytics dashboard adopted by 80% of enterprise accounts within the first quarter."
            ]
        )
        pdf_bytes = create_pdf(mock_data)
        with open("styled_resume_large.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Saved styled_resume_large.pdf")
        
    test_layout()