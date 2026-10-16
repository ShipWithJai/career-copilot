import unittest
from unittest.mock import AsyncMock, patch

from app.services.customizer import (
    ContactInfo,
    EducationEntry,
    ProjectEntry,
    ResumeValidationError,
    TailoredResume,
    TailoredRole,
    TailoringResult,
    create_pdf,
    generate_tailored_resume_data,
    validate,
)


class CustomizerValidationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.base = (
            "Data Analyst | Acme | Jan 2020 - Present\n"
            "Analyzed 10k rows of SQL data.\n"
            "Built dashboards.\n"
            "Bachelor of Science | Example University\n"
            "Project: Sales Dashboard\n"
            "Certification: Tableau Desktop Specialist"
        )
        self.resume = TailoredResume(
            contact=ContactInfo(
                name="Alex Chen",
                email="",
                phone="",
                location="",
                links=[],
            ),
            headline="Data Analyst",
            professional_summary="",
            skill_groups=[],
            experience=[
                TailoredRole(
                    job_title="Data Analyst",
                    company="Acme",
                    location="",
                    dates="Jan 2020 - Present",
                    bullets=["Analyzed sales data."],
                )
            ],
            projects=[ProjectEntry(name="Sales Dashboard", tech="", bullets=[])],
            education=[
                EducationEntry(
                    degree="Bachelor of Science",
                    institution="Example University",
                    dates="",
                    details="",
                )
            ],
            certifications=["Tableau Desktop Specialist"],
        )

    def test_validation_flags_missing_source_entities(self) -> None:
        self.resume.experience[0].job_title = "Invented title"
        self.resume.education[0].institution = "Invented university"
        self.resume.projects[0].name = "Invented project"
        self.resume.certifications[0] = "Invented certification"

        errors, _ = validate(self.resume, self.base)

        self.assertTrue(any("Job title" in error for error in errors))
        self.assertTrue(any("Education institution" in error for error in errors))
        self.assertTrue(any("Project" in error for error in errors))
        self.assertTrue(any("Certification" in error for error in errors))

    def test_validation_rejects_repeated_facts_and_unsupported_filler(self) -> None:
        self.resume.experience[0].bullets = [
            "Analyzed 10k rows of SQL data for operational reporting.",
            "Analyzed 10k rows of SQL data to deliver actionable insights.",
        ]

        errors, _ = validate(self.resume, self.base)

        self.assertTrue(any("repeat the same fact" in error for error in errors))
        self.assertTrue(any("actionable insights" in error for error in errors))

    def test_pdf_renders_with_optional_contact_fields_empty(self) -> None:
        self.assertTrue(create_pdf(self.resume).startswith(b"%PDF-"))

    async def test_wrapper_does_not_return_a_resume_with_unresolved_errors(self) -> None:
        result = TailoringResult(self.resume, errors=["A required source fact is missing."])
        with patch(
            "app.services.customizer.tailor_resume",
            new_callable=AsyncMock,
            return_value=result,
        ):
            with self.assertRaises(ResumeValidationError) as raised:
                await generate_tailored_resume_data(self.base, "A data analyst role.")

        self.assertEqual(raised.exception.errors, result.errors)


if __name__ == "__main__":
    unittest.main()
