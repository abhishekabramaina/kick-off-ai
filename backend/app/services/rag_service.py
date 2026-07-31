import uuid
from typing import List
from sqlalchemy.orm import Session

from ..rag.embeddings import EmbeddingService
from ..rag.chunking import ChunkingService
from ..rag.vector_store import VectorStore
from ..repositories.document_chunk_repo import DocumentChunkRepository

class RAGService:
    def __init__(
        self, 
        embedding_service: EmbeddingService, 
        vector_store: VectorStore,
        chunk_repo: DocumentChunkRepository = DocumentChunkRepository()
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunk_repo = chunk_repo

    def index_employee(self, db: Session, employee_id: int, resume_text: str) -> None:
        """
        Delete old resume index, chunk the resume text, embed all chunks, 
        and save them to the vector database and database metadata storage.
        """
        if not resume_text or not resume_text.strip():
            # If the resume is cleared, simply delete existing indexes
            self.delete_employee_index(db, employee_id)
            return

        # 1. Delete previous indexes to prevent duplicates / stale data
        self.delete_employee_index(db, employee_id)

        # 2. Split resume into semantic sections
        chunks = ChunkingService.chunk_resume(resume_text, employee_id=employee_id)
        if not chunks:
            return

        # 3. Batch generate embeddings for performance
        contents = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(contents, task_type="retrieval_document")

        # 4. Generate unique IDs and metadata for the vector database
        vector_ids = [f"employee_{employee_id}_chunk_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
        vector_metadatas = [
            {
                "source_type": chunk.metadata["source_type"],
                "source_id": chunk.metadata["source_id"],
                "section": chunk.metadata["section"]
            }
            for chunk in chunks
        ]

        # 5. Add to Vector Store (ChromaDB)
        self.vector_store.add(
            ids=vector_ids,
            embeddings=embeddings,
            metadatas=vector_metadatas,
            documents=contents
        )

        # 6. Save metadata and map to SQLite for database reference
        for i, chunk in enumerate(chunks):
            self.chunk_repo.create(
                db=db,
                source_type="resume",
                source_id=employee_id,
                chunk_index=chunk.metadata["chunk_index"],
                content=chunk.content,
                embedding_id=vector_ids[i],
                metadata_dict=chunk.metadata
            )

    def delete_employee_index(self, db: Session, employee_id: int) -> None:
        """
        Delete all indexed resume chunks and vectors for an employee.
        """
        # Delete from Vector Database (ChromaDB) using metadata filter
        self.vector_store.delete(where={"$and": [{"source_type": "resume"}, {"source_id": employee_id}]})
        
        # Delete chunk metadata records from SQLite
        self.chunk_repo.delete_by_source(db, "resume", employee_id)
