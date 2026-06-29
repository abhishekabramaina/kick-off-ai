from sqlalchemy.orm import Session
from .. import models

class MatchRepository:
    """
    Data Access Layer for Candidate Match database operations.
    - Concept: Repository Pattern.
    - Purpose: Encapsulates all SQL logic for matching employees to roles.
    """
    
    def __init__(self, db: Session):
        """
        Initializes the repository with a SQLAlchemy database session.
        """
        self.db = db

    def get_by_role(self, role_id: int):
        """
        Retrieves all matches for a specific role, ordered by score descending.
        - What: SELECT * FROM matches WHERE role_id = role_id ORDER BY score DESC;
        - How: Uses SQLAlchemy order_by and filter logic.
        """
        return self.db.query(models.Match).filter(models.Match.role_id == role_id).order_by(models.Match.score.desc()).all()

    def count_by_role(self, role_id: int):
        """
        Counts the number of existing matches for a role.
        - Why: Used to prevent redundant AI matching calls (Cost/Speed optimization).
        """
        return self.db.query(models.Match).filter(models.Match.role_id == role_id).count()

    def create(self, role_id: int, employee_id: int, score: float, justification: str):
        """
        Creates and persists a new candidate match record.
        - What: INSERT INTO matches (role_id, employee_id, score, justification) VALUES (...);
        - How: Instantiates a models.Match and saves it via self.db.
        """
        db_match = models.Match(
            role_id=role_id,
            employee_id=employee_id,
            score=score,
            justification=justification
        )
        self.db.add(db_match)
        self.db.commit()
        self.db.refresh(db_match)
        return db_match
