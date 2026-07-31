from fastapi import APIRouter, Depends
from typing import List
from .. import schemas
from ..dependencies import get_employee_service
from ..services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/", response_model=List[schemas.Employee])
def list_employees(service: EmployeeService = Depends(get_employee_service)):
    """
    HTTP GET endpoint to list all employees.
    - Contract: Returns a list of all Employee schemas.
    - Delegation: Calls EmployeeService.list_employees().
    """
    return service.list_employees()

@router.post("/", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeBase, 
    service: EmployeeService = Depends(get_employee_service)
):
    """
    HTTP POST endpoint to create a new employee.
    """
    return service.create_employee(
        name=employee.name, 
        resume_text=employee.resume_text, 
        is_on_bench=employee.is_on_bench,
        status=employee.status or "on_bench"
    )

@router.get("/bench", response_model=List[schemas.Employee])
def list_bench(service: EmployeeService = Depends(get_employee_service)):
    """
    HTTP GET endpoint to list all employees currently on the bench.
    """
    return service.get_bench_employees()

@router.get("/{employee_id}", response_model=schemas.Employee)
def read_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    HTTP GET endpoint to retrieve a single employee.
    """
    emp = service.get_employee(employee_id)
    if not emp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.patch("/{employee_id}/status", response_model=schemas.Employee)
def update_employee_status(
    employee_id: int,
    status: str,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    HTTP PATCH endpoint to update a candidate's talent lifecycle status.
    Valid statuses: on_bench, assigned, suspended, archived.
    """
    emp = service.update_status(employee_id, status)
    if not emp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service)
):
    """
    HTTP PUT endpoint to update employee name or resume.
    """
    emp = service.update_profile(employee_id, name=employee.name, resume_text=employee.resume_text)
    if not emp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp
