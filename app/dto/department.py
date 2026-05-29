from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DepartmentDTO(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

class DepartmentDetailDTO(BaseModel):
    department: DepartmentDTO
    employees: List['EmployeeDTO'] = []
    children: List['DepartmentDetailDTO'] = []

    class Config:
        orm_mode = True