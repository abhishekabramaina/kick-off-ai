from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

# Employee Domain Imports
from .repositories.employee_repo import EmployeeRepository
from .services.employee_service import EmployeeService

# RAG Imports
from .rag.embeddings import EmbeddingService
from .rag.chroma_store import ChromaStore
from .services.rag_service import RAGService
from .rag.retriever import Retriever

# Project Domain Imports
from .repositories.project_repo import ProjectRepository
from .services.project_service import ProjectService

# Resourcing Domain Imports
from .repositories.role_repo import RoleRepository
from .repositories.match_repo import MatchRepository
from .services.resourcing_service import ResourcingService

# --- RAG Core Providers ---

def get_embedding_service() -> EmbeddingService:
    """Provides EmbeddingService instance."""
    return EmbeddingService()

def get_vector_store() -> ChromaStore:
    """Provides ChromaStore instance."""
    return ChromaStore()

def get_rag_service(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: ChromaStore = Depends(get_vector_store)
) -> RAGService:
    """Provides RAGService instance."""
    return RAGService(embedding_service=embedding_service, vector_store=vector_store)

def get_retriever(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: ChromaStore = Depends(get_vector_store)
) -> Retriever:
    """Provides Retriever instance."""
    return Retriever(embedding_service=embedding_service, vector_store=vector_store)

# --- Employee Domain Providers ---

def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    """Provides EmployeeRepository instance."""
    return EmployeeRepository(db)

def get_employee_service(
    repo: EmployeeRepository = Depends(get_employee_repo),
    rag_service: RAGService = Depends(get_rag_service)
) -> EmployeeService:
    """Provides EmployeeService instance with RAG indexing support."""
    return EmployeeService(repo, rag_service)


# --- Project Domain Providers ---

def get_project_repo(db: Session = Depends(get_db)) -> ProjectRepository:
    """Provides ProjectRepository instance."""
    return ProjectRepository(db)

def get_project_service(repo: ProjectRepository = Depends(get_project_repo)) -> ProjectService:
    """Provides ProjectService instance."""
    return ProjectService(repo)

# --- Resourcing Domain Providers ---

def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
    """Provides RoleRepository instance."""
    return RoleRepository(db)

def get_match_repo(db: Session = Depends(get_db)) -> MatchRepository:
    """Provides MatchRepository instance."""
    return MatchRepository(db)

def get_resourcing_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    role_repo: RoleRepository = Depends(get_role_repo),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    match_repo: MatchRepository = Depends(get_match_repo),
    retriever: Retriever = Depends(get_retriever)
) -> ResourcingService:
    """
    Provides ResourcingService instance.
    - Concept: Cross-domain Dependency Injection.
    - Why: Orchestrates dependencies from multiple domains (Projects, Employees, Roles, Matches).
    """
    return ResourcingService(project_repo, role_repo, employee_repo, match_repo, retriever)

