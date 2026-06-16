from ..repositories.employee_repo import EmployeeRepository

class EmployeeService:
    """
    Business Logic Layer (BLL) for Employee domain operations.
    - Concept: Service Layer Pattern.
    - Purpose: Coordinates between repositories and enforces business rules (Domain Logic).
    """
    
    def __init__(self, repo: EmployeeRepository):
        """
        Constructor-based Dependency Injection.
        - Why: Injects the EmployeeRepository to decouple business logic from data access logic.
        - How: Stores the repository instance in a local variable self.repo.
        """
        self.repo = repo

    def list_employees(self):
        """
        Coordinates the retrieval of all employee records.
        - What: Orchestrates the request for all employees.
        - Why: Provides a high-level method for the API layer to call.
        - How: Delegates the data retrieval task to the repository.
        """
        return self.repo.get_all()

    def get_bench_employees(self):
        """
        Retrieves employees currently available for project assignment.
        - What: High-level business logic for "Bench" retrieval.
        - Why: Encapsulates the bench status logic so the API doesn't need to know filtering details.
        - How: Calls the repository's bench-specific query method.
        """
        return self.repo.get_on_bench()

    def create_employee(self, name: str, resume_text: str, is_on_bench: bool = True):
        """
        Handles the workflow for onboarding a new employee.
        - What: Coordinates the creation of a new employee entity.
        - Why: Central entry point for all "Employee Creation" logic.
        - How: Delegates persistence to the repository.
        """
        # Note: If we had business validation (e.g., uniqueness checks), it would live here.
        return self.repo.create(name=name, resume_text=resume_text, is_on_bench=is_on_bench)
