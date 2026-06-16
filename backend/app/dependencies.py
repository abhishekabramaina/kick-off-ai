from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

# Employee Domain Imports
from .repositories.employee_repo import EmployeeRepository
from .services.employee_service import EmployeeService

# Project Domain Imports
from .repositories.project_repo import ProjectRepository
from .services.project_service import ProjectService

# --- Employee Domain Providers ---

def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    """
    Dependency provider for EmployeeRepository.
    """
    return EmployeeRepository(db)

def get_employee_service(repo: EmployeeRepository = Depends(get_employee_repo)) -> EmployeeService:
    """
    Dependency provider for EmployeeService.
    """
    return EmployeeService(repo)

# --- Project Domain Providers ---

def get_project_repo(db: Session = Depends(get_db)) -> ProjectRepository:
    """
    Dependency provider for ProjectRepository.
    - Concept: Inversion of Control.
    - Why: Allows the ProjectRepository to be swapped or mocked in tests.
    """
    return ProjectRepository(db)

def get_project_service(repo: ProjectRepository = Depends(get_project_repo)) -> ProjectService:
    """
    Dependency provider for ProjectService.
    - Concept: DI Injection Chain.
    - How: Injects the repository provided by get_project_repo into the service.
    """
    return ProjectService(repo)
