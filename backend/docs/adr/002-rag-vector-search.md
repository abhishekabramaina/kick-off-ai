# ADR-002: Retrieval-Augmented Generation (RAG) for Semantic Candidate Matching

## Status
Accepted

## Context
The current candidate matching workflow in `ResourcingService` evaluates every benched employee against a role by making individual LLM calls (one per candidate). This brute-force approach has several limitations:
- **Cost:** Matching against N candidates requires N LLM calls, each consuming API tokens.
- **Latency:** Each LLM call takes 2-5 seconds. Matching 50 candidates = 100-250 seconds of serial processing.
- **No Semantic Search:** There is no way to query the talent pool with natural language (e.g., "find someone with microservices migration experience").
- **No Reusability:** Parsed resume text is stored but not indexed for retrieval across workflows.

As the talent pool grows beyond tens of candidates, this approach becomes untenable for user experience and cost.

## Decision
We will implement a **Retrieval-Augmented Generation (RAG)** pipeline using a **two-stage matching** approach:

1. **Stage 1 — Vector Retrieval:** Employee resumes are chunked, embedded using Gemini `text-embedding-004`, and stored in a vector database. When matching is triggered, the role JD is embedded and a similarity search retrieves the top-K (default 5-10) most relevant candidate chunks.
2. **Stage 2 — LLM Deep Evaluation:** Only the shortlisted top-K candidates are sent to the LLM for detailed scoring and justification, using the existing `MATCHING_PROMPT`.

### Technology Choices
- **Vector Store (Phase 1):** ChromaDB — embedded, file-based, zero infrastructure. Sufficient for expected scale (100s to low 1000s of candidates).
- **Vector Store (Phase 2, future):** pgvector — when the system migrates to PostgreSQL, the vector store will be consolidated into the relational database.
- **Embedding Model:** Gemini `text-embedding-004` (768 dimensions) — consistent with our existing Google AI ecosystem.
- **Abstraction:** A clean `VectorStore` interface will decouple business logic from the specific vector database implementation, enabling a swap from ChromaDB to pgvector without touching service-layer code.

### Indexing Strategy
Embeddings are generated **at write-time** (when employees are created or resumes are updated), not at query-time. This ensures retrieval is fast (<50ms) at the cost of a slight delay during data ingestion.

## Consequences

### Positive
- **Performance:** Matching time drops from O(N) LLM calls to O(K) where K << N. A 200-candidate pool requires ~5 LLM calls instead of 200.
- **Cost Reduction:** 95%+ reduction in LLM API token usage for matching workflows.
- **Semantic Search:** Enables natural language queries across the talent pool for the first time.
- **Foundation:** Establishes the RAG infrastructure that can be extended to project documents, PRDs, and conversational interfaces.
- **Swappability:** The abstract `VectorStore` interface follows the same Repository pattern established in ADR-001.

### Negative
- **New Dependency:** Introduces ChromaDB as an additional data store alongside SQLite.
- **Embedding Drift:** If the embedding model is changed, all existing vectors must be re-indexed.
- **Eventual Consistency:** There is a brief window after employee creation where the resume is not yet searchable (embedding generation is synchronous but takes ~1 second).

## Compliance
- All vector store interactions must go through the `VectorStore` abstraction — direct ChromaDB calls from services are prohibited.
- The `rag/` module follows the same layered architecture: Services orchestrate, the vector store handles persistence.
- Resume indexing must be triggered automatically on employee create and update — manual indexing is not acceptable for data consistency.
