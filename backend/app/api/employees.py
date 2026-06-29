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
    - Contract: Accepts EmployeeBase schema and returns a full Employee schema.
    - Delegation: Calls EmployeeService.create_employee().
    """
    return service.create_employee(
        name=employee.name, 
        resume_text=employee.resume_text, 
        is_on_bench=employee.is_on_bench
    )

@router.get("/bench", response_model=List[schemas.Employee])
def list_bench(service: EmployeeService = Depends(get_employee_service)):
    """
    HTTP GET endpoint to list all employees currently on the bench.
    - Contract: Returns a filtered list of Employee schemas.
    - Delegation: Calls EmployeeService.get_bench_employees().
    """
    return service.get_bench_employees()
