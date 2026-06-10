# BRAIN: AI-Assisted Project Kickoff & Resourcing

## 🚀 Status: MVP Prototype Complete
The "BRAIN" system is now a functional prototype bridging the gap between client vision and project staffing using AI orchestration.

---

## 🏗️ Architecture Overview
- **Frontend:** Next.js 14 (App Router, TypeScript, Vanilla CSS)
- **Backend:** FastAPI (Python 3.10+, SQLAlchemy, Pydantic)
- **Database:** PostgreSQL (Development: SQLite/kickoff.db)
- **AI Core:** Gemini 1.5 Flash (via `google-generativeai`)

---

## 🛠️ What We've Built So Far

### 1. The Kickoff Loop (Intake & Iteration)
- **Raw Ingestion:** UI for pasting meeting notes/vision.
- **Ambiguity Detection:** AI analyzes notes for contradictions/missing info and generates clarifying questions.
- **Refinement UI:** Multi-step wizard allowing users to clarify AI-flagged points.
- **PRD Generation:** AI synthesizes final notes into a structured Markdown PRD.

### 2. Resourcing Engine
- **Role Extraction:** AI parses the PRD to identify specific roles (e.g., Senior Backend Engineer).
- **Automated JDs:** Context-aware Job Descriptions generated for every identified role.

### 3. Talent Matching (The Onboarding)
- **Internal Bench:** Database of employee resumes and availability.
- **Skill Match Matrix:** AI compares JDs vs. Resumes to provide:
  - **Numeric Match Score (0-100%)**
  - **Textual Justification** (Why they match, where the gaps are).
- **Gap Identification:** System flags roles that cannot be filled from the internal bench.

---

## 📂 Project Structure
```text
BRAIN/
├── frontend/               # Next.js Application
│   ├── src/app/            # Routes (Home, New Project, Bench)
│   ├── src/lib/api.ts      # Backend Communication Layer
│   └── globals.css         # Modern Vanilla CSS Theme
└── backend/                # FastAPI Application
    ├── app/
    │   ├── api/            # Route Handlers (Projects, Resourcing, Employees)
    │   ├── models.py       # SQLAlchemy Schema (Projects, Roles, Employees, Matches)
    │   ├── prompts.py      # AI Prompt Engineering Logic
    │   └── llm_service.py  # Provider-agnostic AI Wrapper
    └── seed_data.py        # Script to populate initial employee bench
```

---

## 📈 Progress Dashboard
| Phase | Feature | Status |
| :--- | :--- | :--- |
| **Phase 1** | Project Setup & Infrastructure | ✅ Complete |
| **Phase 1** | Database Schema & Seed Data | ✅ Complete |
| **Phase 2** | LLM Abstraction Layer (Gemini) | ✅ Complete |
| **Phase 2** | PRD & Ambiguity Logic | ✅ Complete |
| **Phase 2** | Role & Match API Endpoints | ✅ Complete |
| **Phase 3** | Global Design & Layout | ✅ Complete |
| **Phase 3** | Kickoff Wizard UI | ✅ Complete |
| **Phase 3** | Bench & Project Dashboards | ✅ Complete |
| **Phase 4** | Advanced Matching UI | 🏗️ Next Step |

---

## 📝 Next Steps
1. **Match Matrix UI:** Enhance the Resourcing page to show a side-by-side comparison of multiple candidates per role.
2. **Document Upload:** Support PDF/DOCX upload for client notes and employee resumes.
3. **Claude Migration:** Implement the production-tier 
LLM provider (Anthropic) for higher-reasoning PRDs.
