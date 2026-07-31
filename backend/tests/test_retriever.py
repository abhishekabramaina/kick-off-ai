import os
from dotenv import load_dotenv
from app.database import engine, Base, SessionLocal
from app.rag.embeddings import EmbeddingService
from app.rag.chroma_store import ChromaStore
from app.services.rag_service import RAGService
from app.rag.retriever import Retriever

# Load environment
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def test_retriever():
    print("Preparing test database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    emb_service = EmbeddingService()
    vector_store = ChromaStore(collection_name="test_retriever_collection")
    rag_service = RAGService(embedding_service=emb_service, vector_store=vector_store)
    retriever = Retriever(embedding_service=emb_service, vector_store=vector_store)
    
    try:
        # Index candidate 1: Python/FastAPI Backend
        print("Indexing candidate 1 (Backend)...")
        rag_service.index_employee(db, 101, """
        SKILLS
        Python, FastAPI, Postgres, Docker
        EXPERIENCE
        - 4 years building APIs.
        """)
        
        # Index candidate 2: React Frontend
        print("Indexing candidate 2 (Frontend)...")
        rag_service.index_employee(db, 102, """
        SKILLS
        JavaScript, React, CSS, HTML5, Next.js
        EXPERIENCE
        - Frontend developer designing beautiful interfaces.
        """)
        
        # Index candidate 3: Project Manager
        print("Indexing candidate 3 (PM)...")
        rag_service.index_employee(db, 103, """
        SKILLS
        Agile, Scrum, Jira, Leadership
        EXPERIENCE
        - Project manager coordinating developers.
        """)
        
        print("Indexing completed. Querying...")
        
        # Query for a Backend Developer role
        jd = "We need a backend developer with expertise in Python API frameworks like FastAPI, SQL databases, and container tools like Docker."
        print(f"Query JD: '{jd}'")
        
        results = retriever.find_similar_candidates(jd, top_k=3)
        print(f"\nRetrieved {len(results)} matches:")
        for r in results:
            print(f"  - Candidate ID {r['employee_id']} (Score: {r['score']:.4f}) matched section '{r['section']}'")
            print(f"    Text: {r['best_matching_chunk'].strip()[:100]}...")
            
        assert len(results) > 0
        # The Python Developer (ID 101) should be the top match
        assert results[0]["employee_id"] == 101
        print("Backend query matches correctly.")
        
        # Query for Frontend
        jd_fe = "UI engineer specializing in React and Next.js frontend styling."
        results_fe = retriever.find_similar_candidates(jd_fe, top_k=2)
        assert results_fe[0]["employee_id"] == 102
        print("Frontend query matches correctly.")
        
    finally:
        # Clean up
        print("Cleaning indexes...")
        rag_service.delete_employee_index(db, 101)
        rag_service.delete_employee_index(db, 102)
        rag_service.delete_employee_index(db, 103)
        db.close()
        print("ChromaStore and SQLite test collections cleaned up!")

if __name__ == "__main__":
    test_retriever();
