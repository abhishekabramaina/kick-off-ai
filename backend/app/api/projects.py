import io
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

from .. import schemas
from ..dependencies import get_project_service
from ..services.project_service import ProjectService
from ..utils.file_helpers import extract_text_from_bytes
from ..llm_service import get_llm_service, LLMService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/{project_id}/drive-ingest")
async def drive_ingest(
    project_id: int, 
    request: schemas.DriveIngestRequest,
    service: ProjectService = Depends(get_project_service)
):
    """
    Endpoint to ingest a file from Google Drive into a project's raw input.
    - Delegation: Handles Google Drive API I/O and delegates data persistence to ProjectService.
    """
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        creds = Credentials(request.access_token)
        google_service = build("drive", "v3", credentials=creds)

        # Download file
        if request.mime_type == "application/vnd.google-apps.document":
            request_api = google_service.files().export_media(fileId=request.file_id, mimeType="text/plain")
        else:
            request_api = google_service.files().get_media(fileId=request.file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_api)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content = fh.getvalue()

        # Save file locally (Simple IO bound operation)
        file_path = f"uploads/{project_id}_{request.file_name}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text via utility
        extracted_text = extract_text_from_bytes(
            file_content, 
            request.mime_type if request.mime_type != "application/vnd.google-apps.document" else "text/plain"
        )
        
        # Update project domain object via service
        service.update_project_input_from_drive(project_id, request.file_name, extracted_text)

        return {"message": "File ingested successfully", "extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive ingestion failed: {str(e)}")

@router.get("/", response_model=List[schemas.Project])
def list_projects(service: ProjectService = Depends(get_project_service)):
    """
    Lists all projects.
    - Delegation: Calls ProjectService.list_projects().
    """
    return service.list_projects()

@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate, 
    service: ProjectService = Depends(get_project_service)
):
    """
    Creates a new project.
    - Delegation: Calls ProjectService.create_project().
    """
    return service.create_project(name=project.name, raw_input=project.raw_input)

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, service: ProjectService = Depends(get_project_service)):
    """
    Retrieves a single project's details.
    - Delegation: Calls ProjectService.get_project().
    """
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/analyze", response_model=List[dict])
async def analyze_ambiguities(
    project_id: int, 
    service: ProjectService = Depends(get_project_service), 
    llm: LLMService = Depends(get_llm_service)
):
    """
    Triggers AI analysis for project ambiguities.
    - Delegation: Calls ProjectService.analyze_ambiguities().
    """
    result = await service.analyze_ambiguities(project_id, llm)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return result

@router.post("/{project_id}/finalize", response_model=schemas.Project)
async def finalize_prd(
    project_id: int, 
    clarifications: str,
    service: ProjectService = Depends(get_project_service), 
    llm: LLMService = Depends(get_llm_service)
):
    """
    Triggers the generation of the final PRD.
    - Delegation: Calls ProjectService.finalize_prd().
    """
    result = await service.finalize_prd(project_id, clarifications, llm)
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return result
