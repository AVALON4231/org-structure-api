from sqlalchemy.orm import Session
from app.services.employee_service import EmployeeService
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.department_repo import DepartmentRepository
from app.api import schemas

class EmployeeController:
    @staticmethod
    def create(db: Session, department_id: int, data: schemas.EmployeeCreateRequest) -> schemas.EmployeeOut:
        emp_repo = EmployeeRepository(db)
        dept_repo = DepartmentRepository(db)
        service = EmployeeService(emp_repo, dept_repo)
        dto = service.create_employee(department_id, data.full_name, data.position, data.hired_at)
        return schemas.EmployeeOut.from_orm(dto)