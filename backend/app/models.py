from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    raw_input = Column(Text, nullable=True)
    final_prd = Column(Text, nullable=True)
    status = Column(String, default="draft") # draft, refining, finalized
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    roles = relationship("Role", back_populates="project")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    draft_jd = Column(Text, nullable=True)
    status = Column(String, default="draft") # draft, open, filled

    project = relationship("Project", back_populates="roles")
    matches = relationship("Match", back_populates="role")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    resume_text = Column(Text, nullable=True)
    is_on_bench = Column(Boolean, default=True)

    matches = relationship("Match", back_populates="employee")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    score = Column(Float, nullable=True)
    justification = Column(Text, nullable=True)

    role = relationship("Role", back_populates="matches")
    employee = relationship("Employee", back_populates="matches")
