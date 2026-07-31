import os
import asyncio
from dotenv import load_dotenv
from app.database import engine, Base, SessionLocal
from app.repositories.project_repo import ProjectRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.match_repo import MatchRepository
from app.rag.embeddings import EmbeddingService
from app.rag.chroma_store import ChromaStore
from app.rag.retriever import Retriever
from app.services.rag_service import RAGService
from app.services.resourcing_service import ResourcingService
from app.llm_service import GeminiService  # Using our concrete LLM implementation

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

async def test_resourcing_rag_flow():
    print("Preparing test database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Initialize repositories
    proj_repo = ProjectRepository(db)
    role_repo = RoleRepository(db)
    emp_repo = EmployeeRepository(db)
    match_repo = MatchRepository(db)
    
    # Initialize RAG components
    print("Initializing RAG & LLM Services...")
    emb_service = EmbeddingService()
    vector_store = ChromaStore(collection_name="test_resourcing_rag_collection")
    rag_service = RAGService(embedding_service=emb_service, vector_store=vector_store)
    retriever = Retriever(embedding_service=emb_service, vector_store=vector_store)
    llm = GeminiService() # Concrete implementation
    
    resourcing_service = ResourcingService(
        project_repo=proj_repo,
        role_repo=role_repo,
        employee_repo=emp_repo,
        match_repo=match_repo,
        retriever=retriever
    )
    
    # Clean previous potential seed conflicts
    for id_to_del in [201, 202, 203]:
        rag_service.delete_employee_index(db, id_to_del)
        emp_to_del = emp_repo.get_by_id(id_to_del)
        if emp_to_del:
            db.delete(emp_to_del)
    db.commit()
    
    try:
        # Create and Index 3 Candidates
        print("Setting up candidates...")
        # 1. Backend Candidate
        emp_be = emp_repo.create(name="Jane BE Dev", resume_text="SKILLS: Python, FastAPI, SQL, Docker. EXPERIENCE: 5 years building backend APIs.", status="on_bench")
        # Overwrite ID to keep it fixed for this test
        emp_be.id = 201
        db.add(emp_be)
        db.commit()
        rag_service.index_employee(db, emp_be.id, emp_be.resume_text)
        
        # 2. Frontend Candidate
        emp_fe = emp_repo.create(name="Bob FE Dev", resume_text="SKILLS: JavaScript, React, CSS, HTML5. EXPERIENCE: UI developer designing pixel perfect styling.", status="on_bench")
        emp_fe.id = 202
        db.add(emp_fe)
        db.commit()
        rag_service.index_employee(db, emp_fe.id, emp_fe.resume_text)
        
        # 3. Project Manager Candidate
        emp_pm = emp_repo.create(name="Sarah PM", resume_text="SKILLS: Jira, Scrum, Agile, Budgeting. EXPERIENCE: Project manager coordinating engineering teams.", status="on_bench")
        emp_pm.id = 203
        db.add(emp_pm)
        db.commit()
        rag_service.index_employee(db, emp_pm.id, emp_pm.resume_text)
        
        # Create a mock Project and Role
        print("Creating mock project and role...")
        project = proj_repo.create(name="Test RAG Project", raw_input="RAG Project Raw Notes")
        role = role_repo.create(
            project_id=project.id,
            title="Backend Web Engineer",
            draft_jd="We need a Python developer who is expert with FastAPI, SQL databases, and container tools like Docker."
        )
        
        # Run Two-Stage Matching
        print("\nTriggering two-stage candidate matching...")
        matches = await resourcing_service.match_bench_to_role(role.id, llm)
        
        print(f"\nMatching completed. Total Match objects created in database: {len(matches)}")
        for m in matches:
            candidate = emp_repo.get_by_id(m.employee_id)
            print(f"  - Match for {candidate.name} (ID: {m.employee_id})")
            print(f"    Score: {m.score}%")
            print(f"    Justification: {m.justification[:100]}...")
            
        # ASSERTIONS
        # The retriever should have shortlisted ONLY the backend developer (or at least ranked Bob/Sarah so low they aren't in top 1 shortlisted for final LLM review).
        # We configured top_k=5, but we only have 3 on the bench.
        # However, the matching should have scored Jane Dev (ID 201) highest because it's a backend role.
        assert len(matches) > 0
        
        # Verify the database records exist
        db_matches = match_repo.get_by_role(role.id)
        assert len(db_matches) == len(matches)
        print("\nDatabase Match verification passed!")
        
    finally:
        # Clean up
        print("\nCleaning up test entities...")
        for id_to_del in [201, 202, 203]:
            rag_service.delete_employee_index(db, id_to_del)
            emp_to_del = emp_repo.get_by_id(id_to_del)
            if emp_to_del:
                db.delete(emp_to_del)
        if 'project' in locals() and project:
            db.delete(project)
        db.commit()
        db.close()
        print("Cleanup done!")

if __name__ == "__main__":
    asyncio.run(test_resourcing_rag_flow())
