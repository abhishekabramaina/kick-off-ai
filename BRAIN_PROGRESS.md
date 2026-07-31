# BRAIN: AI-Assisted Project Kickoff & Resourcing

## 🚀 Project Status: MVP Transition to Enterprise Core
The "BRAIN" system has successfully evolved from a no-code prototype to a functional custom MVP. We are now establishing the architectural foundation for enterprise scale and distributed processing.

---

## 🏛️ Architecture Overview
- **Frontend:** Next.js 14 (App Router, TypeScript, Vanilla CSS)
- **Backend:** FastAPI (Python 3.10+, SQLAlchemy, Pydantic)
- **Database:** PostgreSQL (Development: SQLite/kickoff.db)
- **AI Core:** Gemini 1.5 Flash (via `google-generativeai`)
- **RAG Pipeline:** ChromaDB (Vector Store), Gemini `text-embedding-004` (Embeddings)
- **Planned:** Celery (Distributed Tasks), pgvector (Production Vector Search).

---

## 📅 Full Project Timeline

### Phase 0: The No-Code MVP (Completed) ✅
- **Goal:** Rapidly validate the business process of AI-driven project resourcing.
- **Tech Stack:** Make.com, Notion, Google Drive, Slack.
- **Outcome:** Proven concept for PRD ingestion, role extraction, and candidate matching.

### Phase 1: Custom Code MVP (Completed) ✅
- **Goal:** Migrate to a custom software stack for control and user experience.
- **Tech Stack:** FastAPI, Next.js, PostgreSQL, Gemini.
- **Outcome:** Functional 2-tier application with PRD generation, role management, and direct talent matching.

### Phase 2: Architectural Foundation & Refactoring (Completed) ✅
- **Goal:** Refactor to enterprise standards (N-Tier) for scalability and testability.
- **Key Milestones:**
  - [x] Establishment of Documentation Standards (ADR, Design Docs).
  - [x] Implement Repository Layer (Data Access Layer).
  - [x] Implement Service Layer (Business Logic Layer).
  - [x] Refactor API Routers to use Dependency Injection.

### Phase 2.5: RAG & Semantic Candidate Matching (In Progress) 🧠
- **Goal:** Replace brute-force LLM matching with two-stage retrieval: vector search + LLM deep evaluation.
- **Key Milestones:**
  - [ ] Embedding Service (Gemini `text-embedding-004`)
  - [ ] Resume Chunking Pipeline (Semantic + Fixed-size)
  - [ ] Vector Store Abstraction + ChromaDB Integration
  - [ ] DocumentChunk Model & Repository
  - [ ] RAG Indexing Service (auto-index on employee create/update)
  - [ ] Semantic Retriever (top-K candidate shortlisting)
  - [ ] Two-Stage Matching in ResourcingService
  - [ ] Seed & End-to-End Validation

### Phase 3: Asynchronous Processing & Scale (Future) 🚀
- **Goal:** Handle long-running LLM tasks without blocking API requests.
- **Key Milestones:** Integrate Redis/RabbitMQ and Celery for background matching and scoring.

### Phase 4: Advanced Search & Optimization (Future) 🧠
- **Goal:** Migrate vector store to pgvector, add document knowledge base, PRD intelligence.
- **Key Milestones:** pgvector migration, document/PRD indexing, hybrid search, Bipartite Matching algorithms.

### Phase 5: Production & CI/CD (Future) 🌐
- **Goal:** Secure, reliable deployment.
- **Key Milestones:** Dockerization, GitHub Actions, Cloud deployment (AWS/GCP).

---

## 📂 Project Structure
```text
BRAIN/
├── frontend/               # Next.js Application
└── backend/                # FastAPI Application
    ├── app/
    │   ├── api/            # Presentation Layer (API Routers)
    │   ├── repositories/   # Data Access Layer (SQLAlchemy Logic)
    │   ├── services/       # Business Logic Layer (Domain Rules)
    │   ├── rag/            # RAG Pipeline (Embeddings, Chunking, Vector Store)
    │   ├── utils/          # Shared Utilities (File Parsing, etc.)
    │   ├── models.py       # SQLAlchemy Schema
    │   ├── schemas.py      # Pydantic Models
    │   ├── prompts.py      # AI Prompt Engineering
    │   └── llm_service.py  # Provider-agnostic AI Wrapper
    ├── chroma_data/         # ChromaDB Persistent Storage
    └── docs/               # Project Documentation (ADRs, Design Docs)
```

---

## 📈 Current Progress Dashboard
| Phase | Feature | Status |
| :--- | :--- | :--- |
| **P2.5** | RAG Architecture Decision (ADR-002) | ✅ Complete |
| **P2.5** | RAG Technical Design Doc | ✅ Complete |
| **P2.5** | Embedding Service (Gemini) | 🔲 Not Started |
| **P2.5** | Resume Chunking Service | 🔲 Not Started |
| **P2.5** | Vector Store (ChromaDB) | 🔲 Not Started |
| **P2.5** | RAG Indexing Pipeline | 🔲 Not Started |
| **P2.5** | Semantic Retriever | 🔲 Not Started |
| **P2.5** | Two-Stage Matching Integration | 🔲 Not Started |
| **P2** | Multi-Tier Architecture ADR | ✅ Complete |
| **P2** | Repository Layer Implementation | ✅ Complete |
| **P2** | Service Layer Implementation | ✅ Complete |
| **P2** | API Router Refactoring | ✅ Complete |
| **P1** | Google Drive Ingestion | ✅ Complete |
| **P1** | PRD & Ambiguity Logic | ✅ Complete |
| **P1** | Bench & Project Dashboards | ✅ Complete |
