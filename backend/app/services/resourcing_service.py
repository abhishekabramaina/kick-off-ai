import json
from ..repositories.project_repo import ProjectRepository
from ..repositories.role_repo import RoleRepository
from ..repositories.employee_repo import EmployeeRepository
from ..repositories.match_repo import MatchRepository
from ..llm_service import LLMService
from .. import prompts, models

class ResourcingService:
    """
    Business Logic Layer (BLL) for Resourcing domain operations.
    - Concept: Cross-Domain Orchestration.
    - Purpose: Coordinates between Project, Role, Employee, and Match repositories 
      to handle role extraction and talent matching.
    """
    
    def __init__(
        self, 
        project_repo: ProjectRepository,
        role_repo: RoleRepository,
        employee_repo: EmployeeRepository,
        match_repo: MatchRepository
    ):
        """
        Constructor-based Dependency Injection.
        - Why: Injects all required repositories to fulfill complex staffing workflows.
        - How: Stores repository instances in local member variables.
        """
        self.project_repo = project_repo
        self.role_repo = role_repo
        self.employee_repo = employee_repo
        self.match_repo = match_repo

    async def extract_roles(self, project_id: int, llm: LLMService):
        """
        Orchestrates the extraction of roles from a finalized PRD.
        - Step 1: Fetch project from repository.
        - Step 2: Guard check - Ensure PRD exists.
        - Step 3: Fetch existing roles to prevent duplicates.
        - Step 4: Call LLM to extract role metadata.
        - Step 5: Save roles via RoleRepository.
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return "project_not_found"
        
        # Guard Clause: PRD must be finalized
        if not project.final_prd:
            return "prd_not_finalized"
        
        # Idempotency: Return existing roles if already extracted
        existing_roles = self.role_repo.get_by_project(project_id)
        if existing_roles:
            return existing_roles

        prompt = prompts.ROLE_EXTRACTION_PROMPT.format(prd_text=project.final_prd)
        response = await llm.generate_text(prompt)
        
        try:
            # Cleaning LLM response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                 response = response.split("```")[1].split("```")[0].strip()
            
            roles_data = json.loads(response)
            
            created_roles = []
            for role_data in roles_data:
                db_role = self.role_repo.create(
                    project_id=project_id,
                    title=role_data['Title'],
                    draft_jd=f"Responsibilities: {role_data['Responsibilities']}\nSkills: {role_data['Key Required Skills']}"
                )
                created_roles.append(db_role)
            
            return created_roles
        except Exception:
            return "failed_to_process"

    def get_role_matches(self, role_id: int):
        """
        Retrieves existing candidate matches for a specific role.
        - Delegation: Simple fetch from MatchRepository.
        """
        return self.match_repo.get_by_role(role_id)

    async def match_bench_to_role(self, role_id: int, llm: LLMService):
        """
        Orchestrates the matching of benched employees against a specific role.
        - Step 1: Fetch role details.
        - Step 2: Optimization - Check if matches already exist.
        - Step 3: Fetch benched employees from EmployeeRepository.
        - Step 4: Iteratively call LLM to score each candidate.
        - Step 5: Persist results via MatchRepository.
        """
        role = self.role_repo.get_by_id(role_id)
        if not role:
            return "role_not_found"
        
        # Optimization: Prevent redundant AI calls
        existing_matches = self.match_repo.get_by_role(role_id)
        if existing_matches:
            return existing_matches

        # Cross-Domain: Using employee_repo to get candidates
        bench_employees = self.employee_repo.get_on_bench()
        
        matches = []
        for emp in bench_employees:
            prompt = prompts.MATCHING_PROMPT.format(jd_text=role.draft_jd, resume_text=emp.resume_text)
            response = await llm.generate_text(prompt)
            
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                
                match_data = json.loads(response)
                
                # Persist Match
                db_match = self.match_repo.create(
                    role_id=role_id,
                    employee_id=emp.id,
                    score=float(match_data['score']),
                    justification=match_data['justification']
                )
                matches.append(db_match)
            except:
                continue # Skip failed individual matches
        
        return matches
