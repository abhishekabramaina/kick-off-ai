import os
from dotenv import load_dotenv
from app.database import engine, Base, SessionLocal
from app.rag.embeddings import EmbeddingService
from app.rag.chroma_store import ChromaStore
from app.services.rag_service import RAGService
from app.repositories.document_chunk_repo import DocumentChunkRepository

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def test_rag_indexing():
    print("Setting up database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Initializing services...")
    emb_service = EmbeddingService()
    vector_store = ChromaStore(collection_name="test_rag_collection")
    rag_service = RAGService(embedding_service=emb_service, vector_store=vector_store)
    
    db = SessionLocal()
    try:
        employee_id = 12345
        resume_text = """
        Jane Doe
        Backend Developer
        
        SKILLS
        Python, FastAPI, SQLite, Docker
        
        EXPERIENCE
        Senior Engineer at TechCorp
        - Built scalable web APIs with FastAPI.
        - Designed database schemas.
        """
        
        print(f"Indexing employee {employee_id}...")
        rag_service.index_employee(db=db, employee_id=employee_id, resume_text=resume_text)
        print("Indexed successfully!")
        
        # Verify in database repository
        chunks = DocumentChunkRepository.get_by_source(db, "resume", employee_id)
        print(f"Relational chunks created: {len(chunks)}")
        assert len(chunks) == 3  # general, skills, experience
        
        # Verify in vector database
        # Create a query search to check if we can query Jane's skills
        print("Querying vector store to verify presence...")
        query_vector = emb_service.embed("FastAPI Docker backend", task_type="retrieval_query")
        results = vector_store.query(query_vector, top_k=5, where={"source_id": employee_id})
        
        print(f"Vector query results count: {len(results)}")
        for r in results:
            print(f"  - Match: {r['id']} (Score: {r['score']:.4f}) -> {r['document'][:50]}...")
            
        assert len(results) > 0
        
        # Clean up
        print("Deleting index...")
        rag_service.delete_employee_index(db, employee_id)
        
        chunks_after = DocumentChunkRepository.get_by_source(db, "resume", employee_id)
        assert len(chunks_after) == 0
        print("Verification passed successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_rag_indexing()
