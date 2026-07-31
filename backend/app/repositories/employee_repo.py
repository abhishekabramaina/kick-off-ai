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

    def get_by_id(self, employee_id: int):
        """
        Retrieves a single employee by ID.
        """
        return self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    def get_all(self):
        """
        Retrieves all employees from the database.
        """
        return self.db.query(models.Employee).all()

    def get_on_bench(self):
        """
        Retrieves employees available on the bench (status='on_bench' or is_on_bench=True).
        """
        return self.db.query(models.Employee).filter(
            (models.Employee.status == "on_bench") | (models.Employee.is_on_bench == True)
        ).filter(models.Employee.status != "archived", models.Employee.status != "suspended", models.Employee.status != "assigned").all()

    def get_by_status(self, status: str):
        """
        Retrieves employees filtered by status.
        """
        return self.db.query(models.Employee).filter(models.Employee.status == status).all()

    def create(self, name: str, resume_text: str, is_on_bench: bool = True, status: str = "on_bench"):
        """
        Creates and persists a new employee record.
        """
        db_emp = models.Employee(name=name, resume_text=resume_text, is_on_bench=is_on_bench, status=status)
        self.db.add(db_emp)
        self.db.commit()
        self.db.refresh(db_emp)
        return db_emp

    def update_status(self, employee_id: int, status: str):
        """
        Updates an employee's talent lifecycle status.
        """
        emp = self.get_by_id(employee_id)
        if not emp:
            return None
        emp.status = status
        emp.is_on_bench = (status == "on_bench")
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def update_profile(self, employee_id: int, name: str = None, resume_text: str = None):
        """
        Updates an employee's profile details.
        """
        emp = self.get_by_id(employee_id)
        if not emp:
            return None
        if name is not None:
            emp.name = name
        if resume_text is not None:
            emp.resume_text = resume_text
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp
