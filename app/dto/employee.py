from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class EmployeeDTO(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date] = None
    created_at: datetime

    class Config:
        orm_mode = True