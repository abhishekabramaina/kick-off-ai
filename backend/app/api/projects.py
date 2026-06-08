from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, prompts
from ..llm_service import get_llm_service, LLMService
import json

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(name=project.name, raw_input=project.raw_input, status="draft")
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/{project_id}/analyze", response_model=List[dict])
async def analyze_ambiguities(
    project_id: int, 
    db: Session = Depends(get_db), 
    llm: LLMService = Depends(get_llm_service)
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    prompt = prompts.AMBIGUITY_DETECTION_PROMPT.format(raw_input=db_project.raw_input)
    response = await llm.generate_text(prompt)
    
    # Try to parse JSON from the LLM response
    try:
        # A simple way to extract JSON if the LLM adds markdown wrappers
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
             response = response.split("```")[1].split("```")[0].strip()
        
        ambiguities = json.loads(response)
        return ambiguities
    except Exception as e:
        # If parsing fails, return the raw response in a structured way for now
        return [{"type": "error", "description": "Failed to parse AI response", "raw": response}]

@router.post("/{project_id}/finalize", response_model=schemas.Project)
async def finalize_prd(
    project_id: int, 
    clarifications: str,
    db: Session = Depends(get_db), 
    llm: LLMService = Depends(get_llm_service)
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    combined_input = f"Original Notes: {db_project.raw_input}\n\nClarifications: {clarifications}"
    prompt = prompts.PRD_GENERATION_PROMPT.format(
        project_name=db_project.name, 
        clarified_input=combined_input
    )
    
    prd_markdown = await llm.generate_text(prompt)
    
    db_project.final_prd = prd_markdown
    db_project.status = "finalized"
    db.commit()
    db.refresh(db_project)
    return db_project
