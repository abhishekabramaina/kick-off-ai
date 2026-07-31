# Technical Design: RAG-Powered Semantic Candidate Matching

## 1. Goal
Replace the brute-force candidate matching workflow (1 LLM call per candidate) with a two-stage pipeline: fast vector retrieval to shortlist top-K candidates, followed by LLM deep evaluation on the shortlist only. This also establishes the RAG foundation for future use cases (document search, PRD intelligence).

## 2. New Architecture Components

### 2.1. Folder Layout
The `backend/app` directory will be expanded with a new `rag/` package:
- `rag/embeddings.py`: Wraps Gemini `text-embedding-004` with batching, retry, and error handling.
- `rag/chunking.py`: Splits text into meaningful chunks (semantic for resumes, fixed-size for documents).
- `rag/vector_store.py`: Abstract base class defining the vector store interface.
- `rag/chroma_store.py`: ChromaDB implementation of the vector store interface.
- `rag/retriever.py`: Orchestrates query embedding, vector search, and result ranking.

Supporting changes:
- `services/rag_service.py`: Business logic for indexing and retrieval orchestration.
- `repositories/document_chunk_repo.py`: Persists chunk metadata in the relational database.
- `models.py`: New `DocumentChunk` SQLAlchemy model.

### 2.2. Data Flow — Indexing (Write Path)
```
Employee Created/Updated
    → resume_text extracted
    → ChunkingService.chunk_resume(text) → List[Chunk]
    → EmbeddingService.embed_batch(chunks) → List[Vector]
    → VectorStore.add(vectors, metadata) → stored in ChromaDB
    → DocumentChunkRepo.save(chunk_metadata) → stored in SQLite
```

### 2.3. Data Flow — Matching (Read Path)
```
POST /resourcing/match/{role_id}
    → Fetch role JD from database
    → EmbeddingService.embed(jd_text) → query_vector
    → VectorStore.query(query_vector, top_k=10, filters={source_type: 'resume'})
    → Group results by employee_id, rank by best chunk similarity
    → For each top-K candidate:
        → LLMService.generate(MATCHING_PROMPT, jd=role_jd, resume=full_resume)
        → Parse score + justification
    → Persist Match records to database
    → Return results
```

## 3. Implementation Details

### 3.1. Embedding Service (`rag/embeddings.py`)
- **Model:** Gemini `text-embedding-004` (768 dimensions)
- **Interface:**
  - `embed(text: str) → List[float]` — Single text embedding
  - `embed_batch(texts: List[str]) → List[List[float]]` — Batch embedding
- **Error Handling:** Retry with exponential backoff on API failures
- **Configuration:** Model name configurable via environment variable `EMBEDDING_MODEL`

### 3.2. Chunking Service (`rag/chunking.py`)
- **Resume Chunking (Semantic):**
  - Splits by section headers (Experience, Skills, Education, Summary, Projects)
  - Uses regex patterns to detect common resume section boundaries
  - Each chunk includes metadata: `{section: "experience", chunk_index: 0}`
  - Fallback: If no sections detected, use fixed-size chunking
- **Fixed-Size Chunking (Generic):**
  - Chunk size: ~500 tokens with 50-token overlap
  - Preserves sentence boundaries (doesn't split mid-sentence)
- **Chunk Data Class:**
  ```python
  @dataclass
  class Chunk:
      content: str
      metadata: dict  # {section, chunk_index, source_type, source_id}
  ```

### 3.3. Vector Store Abstraction (`rag/vector_store.py`)
Abstract base class with methods:
```python
class VectorStore(ABC):
    @abstractmethod
    def add(self, ids: List[str], embeddings: List[List[float]], 
            metadatas: List[dict], documents: List[str]) -> None: ...

    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int = 10,
              where: Optional[dict] = None) -> List[QueryResult]: ...

    @abstractmethod
    def delete(self, ids: Optional[List[str]] = None,
               where: Optional[dict] = None) -> None: ...
```

### 3.4. ChromaDB Implementation (`rag/chroma_store.py`)
- Persistent storage in `backend/chroma_data/` directory
- Collection name: `brain_documents`
- Distance metric: Cosine similarity
- Metadata filtering: Supports `source_type` and `source_id` filters

### 3.5. DocumentChunk Model (`models.py`)
```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    source_type = Column(String(20), nullable=False)    # 'resume' | 'project_doc' | 'prd'
    source_id = Column(Integer, nullable=False)          # employee_id or project_id
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text)                         # JSON string
    embedding_id = Column(String(100))                   # ChromaDB document ID
    created_at = Column(DateTime, default=func.now())
```

### 3.6. RAG Service (`services/rag_service.py`)
Orchestrates the full pipeline:
- `index_employee(employee_id, resume_text)`:
  1. Delete existing chunks for this employee (re-indexing)
  2. Chunk the resume text
  3. Generate embeddings for all chunks
  4. Store in vector store with metadata `{source_type: 'resume', source_id: employee_id}`
  5. Persist chunk metadata to `document_chunks` table
- `find_candidates_for_role(role_jd, top_k=10)`:
  1. Embed the role JD
  2. Query vector store with filter `{source_type: 'resume'}`
  3. Group results by `source_id` (employee_id)
  4. Return top-K unique employees ranked by best chunk similarity

### 3.7. Retriever (`rag/retriever.py`)
- Encapsulates the query → embed → search → rank pipeline
- Handles result deduplication (multiple chunks from same employee)
- Ranking strategy: Best single chunk similarity score per employee

## 4. Integration Points

### 4.1. Employee Service Modification
After `create_employee()` and `update_employee()`:
```python
# In employee_service.py
self.rag_service.index_employee(employee.id, employee.resume_text)
```

### 4.2. Resourcing Service Modification
Replace the brute-force loop in `match_candidates_for_role()`:
```python
# Before (brute-force):
for employee in bench_employees:
    score = llm.match(role_jd, employee.resume_text)

# After (two-stage):
top_candidates = self.rag_service.find_candidates_for_role(role.draft_jd, top_k=10)
for candidate in top_candidates:
    score = llm.match(role_jd, candidate.resume_text)
```

### 4.3. Dependency Injection (`dependencies.py`)
New providers:
- `get_embedding_service() → EmbeddingService`
- `get_vector_store() → VectorStore` (returns `ChromaStore` instance)
- `get_rag_service(embedding_service, vector_store, chunk_repo) → RAGService`

## 5. Migration Strategy
Incremental, step-by-step implementation (10 steps documented in the RAG Plan):
1. Smoke test ChromaDB + embeddings
2. Build embedding service
3. Build chunking service
4. Build vector store abstraction + ChromaDB
5. Add DocumentChunk model + repo
6. Build RAG service (indexing)
7. Hook into employee create/update
8. Build retriever (semantic search)
9. Integrate into resourcing service
10. Seed existing data + end-to-end validation

## 6. Verification Plan
- **Smoke Test:** Verify Gemini embedding API and ChromaDB work end-to-end with test data.
- **Unit Tests:** Test chunking, embedding, and retrieval independently with mock data.
- **Integration Test:** Index seed employees, trigger matching for a role, verify top-K results contain expected candidates.
- **Quality Comparison:** Run matching with RAG vs. brute-force on the same data set and compare result quality.
