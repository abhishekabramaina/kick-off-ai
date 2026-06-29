from sqlalchemy.orm import Session
from .. import models

class ProjectRepository:
    """
    Data Access Layer for Project-related database operations.
    - Concept: Repository Pattern.
    - Purpose: Isolates SQLAlchemy query logic from the business logic layer.
    """
    
    def __init__(self, db: Session):
        """
        Initializes the repository with a SQLAlchemy database session.
        - What: Dependency Injection.
        - Why: Provides the database connection for all methods in the class.
        - How: Stores the session in a local variable self.db.
        """
        self.db = db

    def get_all(self):
        """
        Retrieves all projects from the database.
        - What: SELECT * FROM projects;
        - How: Uses SQLAlchemy's query(models.Project).all() to fetch all records.
        """
        return self.db.query(models.Project).all()

    def get_by_id(self, project_id: int):
        """
        Retrieves a single project by its primary key ID.
        - What: SELECT * FROM projects WHERE id = project_id;
        - Why: Essential for detail views and ensuring a project exists before updates.
        - How: Filters the Project model by ID and returns the first result or None.
        """
        return self.db.query(models.Project).filter(models.Project.id == project_id).first()

    def create(self, name: str, raw_input: str, status: str = "draft"):
        """
        Creates and persists a new project record.
        - What: INSERT INTO projects (name, raw_input, status) VALUES (...);
        - Why: Handles the initial persistence of a project intake.
        - How: Instantiates a models.Project and saves it via self.db session.
        """
        db_project = models.Project(name=name, raw_input=raw_input, status=status)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def save(self, project: models.Project):
        """
        Persists an updated project object to the database.
        - What: UPDATE projects SET ... WHERE id = project.id;
        - Why: Centralizes the update lifecycle (add, commit, refresh) for any project changes.
        - How: Adds the existing project instance back to the session and commits changes.
        """
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
