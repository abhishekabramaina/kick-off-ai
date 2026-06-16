from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .repositories.employee_repo import EmployeeRepository
from .services.employee_service import EmployeeService

def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    """
    Dependency provider for EmployeeRepository.
    - Concept: Inversion of Control (IoC).
    - Why: Centralizes the creation logic for the repository so routers don't need to know how to instantiate it.
    - How: Injects the SQLAlchemy session and returns a new EmployeeRepository instance.
    """
    return EmployeeRepository(db)

def get_employee_service(repo: EmployeeRepository = Depends(get_employee_repo)) -> EmployeeService:
    """
    Dependency provider for EmployeeService.
    - Concept: Dependency Injection (DI) Chain.
    - Why: Decouples the API layer from the service creation logic and its underlying dependencies.
    - How: Injects the repository provided by get_employee_repo and returns an EmployeeService instance.
    """
    return EmployeeService(repo)
