from sqlalchemy.orm import Session
from .. import models

class RoleRepository:
    """
    Data Access Layer for Role-related database operations.
    - Concept: Repository Pattern.
    - Purpose: Encapsulates all SQL logic for project roles.
    """
    
    def __init__(self, db: Session):
        """
        Initializes the repository with a SQLAlchemy database session.
        """
        self.db = db

    def get_by_project(self, project_id: int):
        """
        Retrieves all roles associated with a specific project.
        - What: SELECT * FROM roles WHERE project_id = project_id;
        - How: Uses SQLAlchemy filter logic to fetch all role records.
        """
        return self.db.query(models.Role).filter(models.Role.project_id == project_id).all()

    def get_by_id(self, role_id: int):
        """
        Retrieves a single role by its ID.
        - What: SELECT * FROM roles WHERE id = role_id;
        """
        return self.db.query(models.Role).filter(models.Role.id == role_id).first()

    def create(self, project_id: int, title: str, draft_jd: str, status: str = "draft"):
        """
        Creates and persists a new role record.
        - What: INSERT INTO roles (project_id, title, draft_jd, status) VALUES (...);
        - How: Instantiates a models.Role and saves it via self.db.
        """
        db_role = models.Role(
            project_id=project_id,
            title=title,
            draft_jd=draft_jd,
            status=status
        )
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def save(self, role: models.Role):
        """
        Persists an updated role object.
        """
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
