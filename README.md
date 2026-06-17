# BRAIN: AI-Assisted Project Kickoff & Resourcing

BRAIN is an enterprise-grade AI platform designed to streamline the project kickoff process. It automates PRD ingestion, extracts project requirements, identifies necessary roles, and matches them with available talent (the "Bench") using advanced LLM reasoning.

## 🚀 Key Features

- **AI-Driven PRD Ingestion:** Automatically parse project requirements from documents.
- **Role Extraction:** Identify technical and non-technical roles required for project success.
- **Intelligent Matching:** Match project needs with employee skills and availability.
- **Bench Management:** Track employee skills, seniority, and current project allocations.
- **Multi-Tier Architecture:** Built with scalability and maintainability in mind (N-Tier Backend).

## 🛠️ Tech Stack

- **Frontend:** Next.js 14 (App Router, TypeScript, Vanilla CSS)
- **Backend:** FastAPI (Python 3.10+, SQLAlchemy, Pydantic)
- **Database:** PostgreSQL (supports SQLite for local development)
- **AI Core:** Gemini 1.5 Flash (via `google-generativeai`)
- **Infrastructure:** Docker-ready, designed for distributed tasks with Celery/Redis (Roadmap).

## 📂 Project Structure

```text
BRAIN/
├── frontend/               # Next.js Application
│   ├── src/app/            # App Router pages and layouts
│   └── src/lib/            # API clients and utilities
└── backend/                # FastAPI Application
    ├── app/
    │   ├── api/            # Presentation Layer (API Routers)
    │   ├── repositories/   # Data Access Layer (SQLAlchemy Logic)
    │   ├── services/       # Business Logic Layer (Domain Rules)
    │   ├── utils/          # Shared Utilities (File Parsing, etc.)
    │   ├── models.py       # SQLAlchemy Schema
    │   ├── schemas.py      # Pydantic Models
    │   ├── prompts.py      # AI Prompt Engineering
    │   └── llm_service.py  # Provider-agnostic AI Wrapper
    └── docs/               # Project Documentation (ADRs, Design Docs)
```

## 🚦 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Google Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy google-generativeai pydantic python-dotenv psycopg2-binary
   ```
4. Create a `.env` file in the `backend` directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   DATABASE_URL=postgresql://postgres:postgres@localhost/kickoff_db
   # For SQLite use: sqlite:///./kickoff.db
   ```
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Seeding Initial Data
To populate the database with initial "Bench" data (employees):
1. While in the `backend` directory and with the virtual environment activated:
   ```bash
   python seed_data.py
   ```
   This will add a set of sample employees with diverse skills to your local database.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏛️ Architecture

The backend follows an **N-Tier Architecture** to ensure separation of concerns:
- **Presentation Layer (API):** Handles HTTP requests and response formatting.
- **Service Layer (Business Logic):** Orchestrates domain rules and AI interactions.
- **Data Access Layer (Repository):** Manages database operations.

For more details, see `backend/docs/adr/001-multi-tier-architecture.md`.

## 🗺️ Roadmap
- **Phase 3:** Asynchronous Processing with Celery & Redis.
- **Phase 4:** Vector Search for advanced talent matching.
- **Phase 5:** Production Deployment with Docker & CI/CD.

## 📄 License
Internal Project. All rights reserved.
