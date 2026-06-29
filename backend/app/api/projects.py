import io
import os
import requests
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List

from .. import schemas
from ..dependencies import get_project_service
from ..services.project_service import ProjectService
from ..utils.file_helpers import extract_text_from_bytes
from ..llm_service import get_llm_service, LLMService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/available-files")
async def list_available_files():
    """
    Lists all files currently in the uploads directory.
    """
    if not os.path.exists("uploads"):
        return {"files": []}
    files = os.listdir("uploads")
    return {"files": files}

@router.post("/{project_id}/upload")
async def upload_local_file(
    project_id: int,
    file: UploadFile = File(...),
    service: ProjectService = Depends(get_project_service)
):
    """
    Endpoint to upload a local file and ingest its content.
    """
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        content = await file.read()
        file_path = f"uploads/{project_id}_{file.filename}"
        
        # Ensure directory exists
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(content)

        # Extract text via utility
        extracted_text = extract_text_from_bytes(content, file.content_type)
        
        # Update project domain object
        service.update_project_input_from_drive(project_id, file.filename, extracted_text)

        return {"message": "File uploaded successfully", "extracted_text": extracted_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/{project_id}/ingest-existing")
async def ingest_existing_file(
    project_id: int,
    file_name: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Endpoint to ingest a file that already exists in the uploads directory.
    """
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_path = f"uploads/{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # Extract text (Simplistic MIME detection by extension)
        ext = file_name.split(".")[-1].lower()
        mime_map = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain"
        }
        mime_type = mime_map.get(ext, "text/plain")
        
        extracted_text = extract_text_from_bytes(content, mime_type)
        service.update_project_input_from_drive(project_id, file_name, extracted_text)

        return {"message": "Existing file ingested", "extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

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
        print(f"DEBUG: Starting ingestion for project {project_id}")
        
        # Use requests directly to avoid the 'RefreshError' logic in the Google library
        headers = {"Authorization": f"Bearer {request.access_token}"}
        
        if request.mime_type == "application/vnd.google-apps.document":
            url = f"https://www.googleapis.com/drive/v3/files/{request.file_id}/export?mimeType=text/plain"
        else:
            url = f"https://www.googleapis.com/drive/v3/files/{request.file_id}?alt=media"

        print(f"DEBUG: Streaming download from {url}")
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code != 200:
            # Fallback: if alt=media fails, it might be a Google-native file that needs export
            if request.mime_type != "application/vnd.google-apps.document":
                print(f"DEBUG: Primary download failed ({response.status_code}). Trying export fallback...")
                url = f"https://www.googleapis.com/drive/v3/files/{request.file_id}/export?mimeType=text/plain"
                response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code != 200:
                raise Exception(f"Google Drive API error ({response.status_code}): {response.text}")

        fh = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024 * 1024): # 1MB chunks
            if chunk:
                fh.write(chunk)
        
        file_content = fh.getvalue()
        print(f"DEBUG: File downloaded, size: {len(file_content)} bytes")

        # Save file locally (Simple IO bound operation)
        file_path = f"uploads/{project_id}_{request.file_name}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text via utility
        print(f"DEBUG: Extracting text from {request.mime_type}")
        extracted_text = extract_text_from_bytes(
            file_content, 
            request.mime_type if request.mime_type != "application/vnd.google-apps.document" else "text/plain"
        )
        
        # Update project domain object via service
        print(f"DEBUG: Updating project {project_id} in database")
        service.update_project_input_from_drive(project_id, request.file_name, extracted_text)

        print(f"DEBUG: Ingestion successful")
        return {"message": "File ingested successfully", "extracted_text": extracted_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
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
