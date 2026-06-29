from sqlalchemy.orm import Session
from .. import models

class EmployeeRepository:
    """
    Data Access Layer for Employee-related database operations.
    - Concept: Repository Pattern.
    - Purpose: Decouples the SQL logic from the business logic.
    """
    
    def __init__(self, db: Session):
        """
        Initializes the repository with a SQLAlchemy database session.
        - What: Dependency Injection.
        - Why: To allow all methods in this class to share the same DB connection.
        - How: Stores the session in a local variable self.db.
        """
        self.db = db

    def get_all(self):
        """
        Retrieves all employees from the database.
        - What: SELECT * FROM employees;
        - Why: Moves database-specific syntax out of the API layer.
        - How: Uses SQLAlchemy's query(models.Employee).all() to fetch all records.
        """
        return self.db.query(models.Employee).all()

    def get_on_bench(self):
        """
        Retrieves only employees currently on the bench.
        - What: SELECT * FROM employees WHERE is_on_bench = true;
        - Why: Centralizes the filter logic for "bench status" in one place.
        - How: Filters the Employee model by the is_on_bench boolean column.
        """
        return self.db.query(models.Employee).filter(models.Employee.is_on_bench == True).all()

    def create(self, name: str, resume_text: str, is_on_bench: bool = True):
        """
        Creates and persists a new employee record.
        - What: INSERT INTO employees (name, resume_text, is_on_bench) VALUES (...);
        - Why: Handles the complete lifecycle (add, commit, refresh) in one transaction.
        - How: Instantiates a models.Employee and saves it via self.db session.
        """
        db_emp = models.Employee(name=name, resume_text=resume_text, is_on_bench=is_on_bench)
        self.db.add(db_emp)
        self.db.commit()
        self.db.refresh(db_emp)
        return db_emp
