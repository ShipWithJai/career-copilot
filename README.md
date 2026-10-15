# Career Copilot - Backend API

Career Copilot is a FastAPI-based web application that automates the job search and resume tailoring process. It uses asynchronous background workers to parse resumes, fetch live job postings, and dynamically generate PDF resumes tailored to specific job descriptions using Google Gemini.

## System Architecture

*   **FastAPI:** Serves as the primary asynchronous web server and traffic controller.
*   **Celery:** Background worker engine for handling CPU-bound and I/O-heavy tasks (PDF generation, bulk job fetching) without blocking the web server.
*   **Redis:** Message broker and result backend. Facilitates communication between FastAPI and Celery.
*   **SQLAlchemy:** Asynchronous ORM for database operations.
*   **Google GenAI:** Powers the intelligent resume tailoring and parsing logic.

## Key Features

*   **Resume Parsing:** Extracts text from uploaded PDF resumes using PyPDF2 and structures the data using LLMs.
*   **Scheduled Job Ingestion:** Automatically fetches job listings from external APIs (e.g., Adzuna) at scheduled intervals using Celery Beat.
*   **Asynchronous PDF Generation:** Generates custom-tailored PDFs in the background. Converts raw binary to Base64 for safe transport via Redis.
*   **Polling API:** Provides endpoints for the frontend to dispatch long-running tasks and poll for their status non-blockingly.

## Local Setup

### 1. Prerequisites
*   Python 3.10+
*   Redis Server (running locally on port 6379)

### 2. Installation
Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```text
GEMINI_API_KEY=your_google_genai_key_here
# Add database URLs and other required keys here
```

## Running the Services

To run the full application locally, you need three separate terminal windows active simultaneously.

**Terminal 1: Start Redis Server**
*(Ensure Redis is installed on your system)*
```bash
redis-server
```

**Terminal 2: Start the Celery Worker**
*(From your project root folder, inside your activated virtual environment)*
```bash
celery -A app.core.celery_app worker --loglevel=info
```

**Terminal 3: Start the FastAPI Server**
*(From your project root folder, inside your activated virtual environment)*
```bash
uvicorn app.main:app --reload
```

## API Documentation
Once the FastAPI server is running, navigate to `http://127.0.0.1:8000/docs` in your browser to access the interactive Swagger UI and test the endpoints.