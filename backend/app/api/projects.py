from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, prompts
from ..llm_service import get_llm_service, LLMService
import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import PyPDF2
import docx

router = APIRouter(prefix="/projects", tags=["projects"])

def extract_text_from_bytes(content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join([page.extract_text() for page in reader.pages])
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    elif "text/" in mime_type or mime_type == "application/vnd.google-apps.document":
        return content.decode("utf-8")
    return ""

@router.post("/{project_id}/drive-ingest")
async def drive_ingest(
    project_id: int, 
    request: schemas.DriveIngestRequest,
    db: Session = Depends(get_db)
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        creds = Credentials(request.access_token)
        service = build("drive", "v3", credentials=creds)

        # Download file
        if request.mime_type == "application/vnd.google-apps.document":
            # Google Docs need to be exported
            request_api = service.files().export_media(fileId=request.file_id, mimeType="text/plain")
        else:
            request_api = service.files().get_media(fileId=request.file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_api)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content = fh.getvalue()

        # Save file locally
        file_path = f"uploads/{project_id}_{request.file_name}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text
        extracted_text = extract_text_from_bytes(file_content, request.mime_type if request.mime_type != "application/vnd.google-apps.document" else "text/plain")
        
        # Update project input
        current_input = db_project.raw_input or ""
        db_project.raw_input = f"{current_input}\n\n[Ingested from Drive: {request.file_name}]\n{extracted_text}"
        db.commit()
        db.refresh(db_project)

        return {"message": "File ingested successfully", "extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive ingestion failed: {str(e)}")

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
