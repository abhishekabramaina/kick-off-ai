from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/", response_model=List[schemas.Employee])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@router.post("/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeBase, db: Session = Depends(get_db)):
    db_emp = models.Employee(
        name=employee.name, 
        resume_text=employee.resume_text, 
        is_on_bench=employee.is_on_bench
    )
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

@router.get("/bench", response_model=List[schemas.Employee])
def list_bench(db: Session = Depends(get_db)):
    return db.query(models.Employee).filter(models.Employee.is_on_bench == True).all()
