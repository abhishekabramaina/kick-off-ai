from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, prompts
from ..llm_service import get_llm_service, LLMService
import json

router = APIRouter(prefix="/resourcing", tags=["resourcing"])

@router.post("/extract-roles/{project_id}", response_model=List[schemas.Role])
async def extract_roles(
    project_id: int, 
    db: Session = Depends(get_db), 
    llm: LLMService = Depends(get_llm_service)
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Return existing roles if already extracted
    existing_roles = db.query(models.Role).filter(models.Role.project_id == project_id).all()
    if existing_roles:
        return existing_roles

    if not db_project.final_prd:
        raise HTTPException(status_code=400, detail="PRD must be finalized before extracting roles")
    
    prompt = prompts.ROLE_EXTRACTION_PROMPT.format(prd_text=db_project.final_prd)
    response = await llm.generate_text(prompt)
    
    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
             response = response.split("```")[1].split("```")[0].strip()
        
        roles_data = json.loads(response)
        
        created_roles = []
        for role_data in roles_data:
            db_role = models.Role(
                project_id=project_id,
                title=role_data['Title'],
                draft_jd=f"Responsibilities: {role_data['Responsibilities']}\nSkills: {role_data['Key Required Skills']}",
                status="draft"
            )
            db.add(db_role)
            created_roles.append(db_role)
        
        db.commit()
        for r in created_roles: db.refresh(r)
        return created_roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process roles: {str(e)}")

@router.get("/matches/{role_id}", response_model=List[schemas.Match])
def get_matches(role_id: int, db: Session = Depends(get_db)):
    return db.query(models.Match).filter(models.Match.role_id == role_id).order_by(models.Match.score.desc()).all()

@router.post("/match/{role_id}")
async def match_bench(
    role_id: int,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Only match if matches don't exist yet to save API calls
    existing_matches = db.query(models.Match).filter(models.Match.role_id == role_id).count()
    if existing_matches > 0:
        return {"message": "Matches already exist"}

    # Get all employees on bench
    bench_employees = db.query(models.Employee).filter(models.Employee.is_on_bench == True).all()
    
    matches = []
    for emp in bench_employees:
        prompt = prompts.MATCHING_PROMPT.format(jd_text=db_role.draft_jd, resume_text=emp.resume_text)
        response = await llm.generate_text(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            
            match_data = json.loads(response)
            
            db_match = models.Match(
                role_id=role_id,
                employee_id=emp.id,
                score=float(match_data['score']),
                justification=match_data['justification']
            )
            db.add(db_match)
            matches.append(db_match)
        except:
            continue # Skip failed matches for now
            
    db.commit()
    return {"message": f"Successfully processed {len(matches)} matches"}
