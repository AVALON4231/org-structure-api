from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import date, datetime

# --- Запросы ---
class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @validator("name")
    def trim_name(cls, v):
        return v.strip()

class DepartmentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @validator("name")
    def trim_name(cls, v):
        return v.strip() if v else v

class EmployeeCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    hired_at: Optional[date] = None

    @validator("full_name", "position")
    def trim_strings(cls, v):
        return v.strip()

# --- Ответы ---
class DepartmentOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

class EmployeeOut(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date] = None
    created_at: datetime

    class Config:
        orm_mode = True

class DepartmentDetailOut(BaseModel):
    department: DepartmentOut
    employees: List[EmployeeOut] = []
    children: List['DepartmentDetailOut'] = []

    class Config:
        orm_mode = True