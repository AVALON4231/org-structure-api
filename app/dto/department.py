from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class DepartmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int] = None
    created_at: datetime

class DepartmentDetailDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department: DepartmentDTO
    employees: List['EmployeeDTO'] = []
    children: List['DepartmentDetailDTO'] = []