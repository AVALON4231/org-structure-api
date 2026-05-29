from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

class EmployeeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date] = None
    created_at: datetime