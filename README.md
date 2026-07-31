# Project Brain: AI-Assisted Distributed Staffing Engine

## 🚀 Overview
**Project Brain** is an enterprise-grade backend system designed to orchestrate the complex workflow of project kickoff and team resourcing. It automates the ingestion of project requirements, resolves ambiguities using Large Language Models (LLMs), generates finalized Product Requirement Documents (PRDs), extracts necessary roles, and algorithmically matches candidates from a bench pool to those roles.

Originally prototyped using no-code tools (Make.com, Notion), this system has been re-architected into a robust, custom **Multi-Tiered Python application** designed for scalability, testability, and fault tolerance.

---

## 🏛️ System Architecture

The backend is built on **FastAPI** and **SQLAlchemy**, strictly adhering to **Domain-Driven Design (DDD)** and an **N-Tier Architecture**. This decouples presentation logic from business rules and data access, ensuring a highly testable and maintainable codebase.

### **Core Layers**
1. **Presentation Layer (API Routers):** "Thin Controllers" that handle HTTP requests, validate input schemas (Pydantic), and delegate all logic to the Service layer.
2. **Business Logic Layer (Services):** Orchestrates complex workflows, enforces domain rules, and coordinates external LLM API calls.
3. **Data Access Layer (Repositories):** Encapsulates all SQLAlchemy logic, abstracting database interactions (PostgreSQL/SQLite) behind clean interfaces.

### **Engineering Principles Applied**
- **Separation of Concerns (SoC):** Distinct boundaries between API, Business Logic, and Data Persistence.
- **Dependency Injection (DI) & Inversion of Control (IoC):** Repositories and Services are injected at runtime via FastAPI's `Depends` system, allowing for complete mockability during unit testing.
- **Single Responsibility Principle (SRP):** Technical parsing logic (e.g., extracting text from binary PDFs/DOCX files) is isolated in a dedicated `utils/` package.

---

## ⚙️ Tech Stack
- **Language:** Python 3.10+
- **API Framework:** FastAPI
- **Database ORM:** SQLAlchemy (Async/Sync)
- **Data Validation:** Pydantic
- **AI Orchestration:** Google Gemini 1.5 Flash (via `google-generativeai`)
- **RAG Pipeline:** ChromaDB (Vector Store), Gemini `text-embedding-004` (Embeddings)
- **Document Processing:** PyPDF2, python-docx
- **Frontend (Client):** Next.js 14, React, TypeScript (Monorepo setup)

---

## 🧠 Core Domains & Workflows

### 1. Project Domain (`ProjectService`)
- **Drive Ingestion:** Securely downloads and extracts text from client requirements via Google Drive API.
- **Ambiguity Detection:** Passes raw client notes to an LLM to identify missing technical or business constraints.
- **PRD Generation:** Synthesizes client notes and clarifications into a structured, finalized Product Requirements Document.

### 2. Employee Domain (`EmployeeService`)
- Manages the lifecycle of talent pool data (resumes, skills).
- Tracks employee availability and "Bench" status.

### 3. Resourcing Domain (`ResourcingService`)
- **Cross-Domain Orchestration:** Interacts with Project, Role, Employee, and Match repositories.
- **Role Extraction:** Uses LLMs to analyze finalized PRDs and automatically generate required job descriptions and technical skill sets.
- **Two-Stage Matching:** Uses RAG-powered semantic retrieval to shortlist top-K candidates via vector similarity, then LLM deep evaluation for scoring and justification.

### 4. RAG & Semantic Search (`RAGService`)
- **Resume Indexing:** Automatically chunks and embeds employee resumes at write-time using Gemini `text-embedding-004`.
- **Vector Store:** ChromaDB stores embeddings for fast cosine similarity retrieval (<50ms).
- **Semantic Retrieval:** Natural language queries against the talent pool (e.g., "microservices experience") return ranked candidates.

---

## 🗺️ Roadmap & Future Enhancements

The system is designed with extensibility in mind to handle incredible scale and speed.

- **Phase 2.5: RAG & Semantic Candidate Matching (In Progress):**
  - **Goal:** Replace brute-force LLM matching with two-stage retrieval (vector search + LLM deep evaluation).
  - **Implementation:** ChromaDB vector store, Gemini embeddings, semantic resume chunking, top-K retrieval pipeline.
- **Phase 3: Asynchronous Distributed Processing:**
  - **Goal:** Offload long-running LLM batch requests (e.g., scoring 100+ candidates) from the main API thread.
  - **Implementation:** Integration of a Message Broker (Redis/RabbitMQ) and distributed task workers (Celery).
- **Phase 4: Advanced Search & Algorithms:**
  - **Goal:** Migrate vector store to pgvector, extend RAG to project documents and PRDs.
  - **Implementation:** pgvector migration, document knowledge base, hybrid search, Bipartite matching for global bench allocation.
- **Phase 5: Cloud Deployment:**
  - **Implementation:** Dockerization, CI/CD via GitHub Actions, and deployment to AWS.

---

## 📜 Documentation
- Complete project timeline and status tracking available in `BRAIN_PROGRESS.md`.
- Architecture Decision Records (ADRs) and Technical Design documents are maintained in `backend/docs/`.
