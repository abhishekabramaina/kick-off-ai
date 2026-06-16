import json
from ..repositories.project_repo import ProjectRepository
from ..llm_service import LLMService
from .. import prompts, models

class ProjectService:
    """
    Business Logic Layer (BLL) for Project domain operations.
    - Concept: Service Orchestration.
    - Purpose: Coordinates between repositories and LLM services to manage the project lifecycle.
    """
    
    def __init__(self, repo: ProjectRepository):
        """
        Constructor-based Dependency Injection.
        - Why: Injects the ProjectRepository to decouple business logic from data access.
        - How: Stores the repository instance in a local variable self.repo.
        """
        self.repo = repo

    def list_projects(self):
        """
        Retrieves all project records.
        - Delegation: Simple fetch from the repository.
        """
        return self.repo.get_all()

    def get_project(self, project_id: int):
        """
        Retrieves a specific project by ID.
        - Delegation: Simple fetch from the repository.
        """
        return self.repo.get_by_id(project_id)

    def create_project(self, name: str, raw_input: str):
        """
        Handles the creation of a new project.
        - Delegation: Simple creation via the repository.
        """
        return self.repo.create(name=name, raw_input=raw_input)

    async def analyze_ambiguities(self, project_id: int, llm: LLMService):
        """
        Orchestrates the AI-driven ambiguity detection workflow.
        - Step 1: Fetch project data from repository.
        - Step 2: Format prompt and call LLM service.
        - Step 3: Parse and clean the JSON response.
        - Why: Removes AI parsing logic from the API layer.
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        prompt = prompts.AMBIGUITY_DETECTION_PROMPT.format(raw_input=project.raw_input)
        response = await llm.generate_text(prompt)
        
        # Internal Parsing Logic
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                 response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except Exception:
            # Fallback for parsing failures
            return [{"type": "error", "description": "Failed to parse AI response", "raw": response}]

    async def finalize_prd(self, project_id: int, clarifications: str, llm: LLMService):
        """
        Orchestrates the final PRD generation workflow.
        - Step 1: Combine original input with clarifications.
        - Step 2: Call LLM for structured PRD generation.
        - Step 3: Update project state (PRD text, status) and persist.
        - Why: Encapsulates the state transition from "draft" to "finalized".
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        combined_input = f"Original Notes: {project.raw_input}\n\nClarifications: {clarifications}"
        prompt = prompts.PRD_GENERATION_PROMPT.format(
            project_name=project.name, 
            clarified_input=combined_input
        )
        
        prd_markdown = await llm.generate_text(prompt)
        
        # Update Domain Object
        project.final_prd = prd_markdown
        project.status = "finalized"
        
        # Persist through repository
        return self.repo.save(project)

    def update_project_input_from_drive(self, project_id: int, file_name: str, extracted_text: str):
        """
        Handles the domain logic for appending ingested Drive content.
        - Why: Ensures the formatting of appended notes is consistent.
        """
        project = self.get_project(project_id)
        if not project:
            return None
            
        current_input = project.raw_input or ""
        project.raw_input = f"{current_input}\n\n[Ingested from Drive: {file_name}]\n{extracted_text}"
        
        return self.repo.save(project)
