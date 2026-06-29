from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .. import schemas
from ..dependencies import get_resourcing_service
from ..services.resourcing_service import ResourcingService
from ..llm_service import get_llm_service, LLMService

router = APIRouter(prefix="/resourcing", tags=["resourcing"])

@router.post("/extract-roles/{project_id}", response_model=List[schemas.Role])
async def extract_roles(
    project_id: int, 
    service: ResourcingService = Depends(get_resourcing_service), 
    llm: LLMService = Depends(get_llm_service)
):
    """
    Endpoint to extract roles from a finalized PRD.
    - Concept: Thin Controller.
    - Delegation: Orchestrates the request by calling ResourcingService.extract_roles().
    """
    result = await service.extract_roles(project_id, llm)
    
    # Handle Service Results
    if result == "project_not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    if result == "prd_not_finalized":
        raise HTTPException(status_code=400, detail="PRD must be finalized before extracting roles")
    if result == "failed_to_process":
        raise HTTPException(status_code=500, detail="Failed to process roles")
        
    return result

@router.get("/matches/{role_id}", response_model=List[schemas.Match])
def get_matches(
    role_id: int, 
    service: ResourcingService = Depends(get_resourcing_service)
):
    """
    Endpoint to retrieve candidate matches for a role.
    - Delegation: Simple delegation to ResourcingService.get_role_matches().
    """
    return service.get_role_matches(role_id)

@router.post("/match/{role_id}", response_model=List[schemas.Match])
async def match_bench(
    role_id: int,
    service: ResourcingService = Depends(get_resourcing_service),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Endpoint to trigger candidate matching for a specific role.
    - Delegation: Orchestrates the request by calling ResourcingService.match_bench_to_role().
    """
    result = await service.match_bench_to_role(role_id, llm)
    
    # Handle Service Results
    if result == "role_not_found":
        raise HTTPException(status_code=404, detail="Role not found")
        
    return result
