from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

# Employee Domain Imports
from .repositories.employee_repo import EmployeeRepository
from .services.employee_service import EmployeeService

# Project Domain Imports
from .repositories.project_repo import ProjectRepository
from .services.project_service import ProjectService

# Resourcing Domain Imports
from .repositories.role_repo import RoleRepository
from .repositories.match_repo import MatchRepository
from .services.resourcing_service import ResourcingService

# --- Employee Domain Providers ---

def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    """Provides EmployeeRepository instance."""
    return EmployeeRepository(db)

def get_employee_service(repo: EmployeeRepository = Depends(get_employee_repo)) -> EmployeeService:
    """Provides EmployeeService instance."""
    return EmployeeService(repo)

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
    match_repo: MatchRepository = Depends(get_match_repo)
) -> ResourcingService:
    """
    Provides ResourcingService instance.
    - Concept: Cross-domain Dependency Injection.
    - Why: Orchestrates dependencies from multiple domains (Projects, Employees, Roles, Matches).
    """
    return ResourcingService(project_repo, role_repo, employee_repo, match_repo)
