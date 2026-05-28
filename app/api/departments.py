from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from typing import Optional

router = APIRouter()

@router.post("/", response_model=schemas.DepartmentOut, status_code=201)
def create_department(data: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, data)

@router.post("/{department_id}/employees/", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(
    department_id: int = Path(..., alias="id"),
    data: schemas.EmployeeCreate = ...,
    db: Session = Depends(get_db)
):
    return crud.create_employee(db, department_id, data)

@router.get("/{department_id}", response_model=schemas.DepartmentDetail)
def get_department(
    department_id: int = Path(..., alias="id"),
    depth: int = Query(1, ge=0, le=5),
    include_employees: bool = True,
    db: Session = Depends(get_db)
):
    return crud.get_department_detail(db, department_id, depth, include_employees)

@router.patch("/{department_id}", response_model=schemas.DepartmentOut)
def update_department(
    department_id: int = Path(..., alias="id"),
    data: schemas.DepartmentUpdate = ...,
    db: Session = Depends(get_db)
):
    return crud.update_department(db, department_id, data)

@router.delete("/{department_id}", status_code=204)
def delete_department(
    department_id: int = Path(..., alias="id"),
    mode: str = Query(..., regex="^(cascade|reassign)$"),
    reassign_to_department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    crud.delete_department(db, department_id, mode, reassign_to_department_id)
    return