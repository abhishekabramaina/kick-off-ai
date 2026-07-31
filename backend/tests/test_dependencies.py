import os
from dotenv import load_dotenv
from app.database import engine, Base, SessionLocal
from app.dependencies import get_employee_service, get_rag_service
from app.repositories.document_chunk_repo import DocumentChunkRepository

# Load environment
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def test_wiring():
    print("Preparing test database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Resolve services
        print("Resolving EmployeeService via dependencies...")
        # Since dependencies use Depends which are resolved by FastAPI, we will mock the dependencies manually
        from app.repositories.employee_repo import EmployeeRepository
        from app.rag.embeddings import EmbeddingService
        from app.rag.chroma_store import ChromaStore
        from app.services.rag_service import RAGService
        from app.services.employee_service import EmployeeService
        
        emp_repo = EmployeeRepository(db)
        emb_service = EmbeddingService()
        vector_store = ChromaStore(collection_name="test_wiring_collection")
        rag_service = RAGService(embedding_service=emb_service, vector_store=vector_store)
        
        employee_service = EmployeeService(emp_repo, rag_service)
        
        # Test creation triggers RAG indexing
        print("Creating a new employee profile to test automatic indexing...")
        name = "Dependency Test Candidate"
        resume_text = """
        EXPERIENCE
        - 3 years as a Cloud Solutions Architect.
        - Managed Kubernetes clusters.
        
        SKILLS
        Kubernetes, AWS, Terraform, Cloud, Go
        """
        
        emp = employee_service.create_employee(
            name=name,
            resume_text=resume_text,
            is_on_bench=True,
            status="on_bench"
        )
        print(f"Employee created with ID: {emp.id}")
        
        # Verify chunks exist in DB
        chunks = DocumentChunkRepository.get_by_source(db, "resume", emp.id)
        print(f"Relational chunks created: {len(chunks)}")
        assert len(chunks) == 2
        
        # Verify in Chroma
        print("Querying ChromaStore to verify presence...")
        query_vector = emb_service.embed("Kubernetes cloud architecture", task_type="retrieval_query")
        results = vector_store.query(query_vector, top_k=5, where={"source_id": emp.id})
        print(f"Vector search matched chunks: {len(results)}")
        assert len(results) > 0
        for r in results:
            print(f"  - Match: {r['id']} (Score: {r['score']:.4f})")
            
        # Test profile updates triggers indexing too
        print("Updating employee resume to test re-indexing...")
        new_resume = """
        SKILLS
        Rust, WebAssembly, Backend
        """
        employee_service.update_profile(employee_id=emp.id, resume_text=new_resume)
        
        # Verify updated chunks
        chunks_after = DocumentChunkRepository.get_by_source(db, "resume", emp.id)
        print(f"Relational chunks after update: {len(chunks_after)}")
        assert len(chunks_after) == 1  # skills section only
        
        # Clean up
        print("Cleaning up test candidate and indexes...")
        rag_service.delete_employee_index(db, emp.id)
        db.delete(emp)
        db.commit()
        print("Test database clean!")
        
        print("\nWiring verification test passed successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_wiring()
