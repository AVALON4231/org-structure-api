from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api import schemas
from app.controllers.department_controller import DepartmentController
from app.controllers.employee_controller import EmployeeController

router = APIRouter()

@router.post("/", response_model=schemas.DepartmentOut, status_code=201)
def create_department(data: schemas.DepartmentCreateRequest, db: Session = Depends(get_db)):
    return DepartmentController.create(db, data)

@router.get("/{department_id}", response_model=schemas.DepartmentDetailOut)
def get_department(
    department_id: int = Path(..., alias="department_id"),
    depth: int = Query(1, ge=0, le=5),
    include_employees: bool = True,
    db: Session = Depends(get_db)
):
    return DepartmentController.get(db, department_id, depth, include_employees)

@router.patch("/{department_id}", response_model=schemas.DepartmentOut)
def update_department(
    department_id: int = Path(..., alias="department_id"),
    data: schemas.DepartmentUpdateRequest = ...,
    db: Session = Depends(get_db)
):
    return DepartmentController.update(db, department_id, data)

@router.delete("/{department_id}", status_code=204)
def delete_department(
    department_id: int = Path(..., alias="department_id"),
    mode: str = Query(..., regex="^(cascade|reassign)$"),
    reassign_to_department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    DepartmentController.delete(db, department_id, mode, reassign_to_department_id)

@router.post("/{department_id}/employees/", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(
    department_id: int = Path(..., alias="department_id"),
    data: schemas.EmployeeCreateRequest = ...,
    db: Session = Depends(get_db)
):
    return EmployeeController.create(db, department_id, data)