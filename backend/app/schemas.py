from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    raw_input: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    final_prd: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    title: str
    draft_jd: Optional[str] = None

class RoleCreate(RoleBase):
    project_id: int

class Role(RoleBase):
    id: int
    project_id: int
    status: str

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    name: str
    resume_text: Optional[str] = None
    is_on_bench: bool = True

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    role_id: int
    employee_id: int
    score: Optional[float] = None
    justification: Optional[str] = None

class Match(MatchBase):
    id: int

    class Config:
        from_attributes = True

class DriveIngestRequest(BaseModel):
    file_id: str
    access_token: str
    file_name: str
    mime_type: str
