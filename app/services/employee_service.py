from app.repositories.employee_repo import EmployeeRepository
from app.validators.employee_validator import EmployeeValidator
from app.repositories.department_repo import DepartmentRepository
from app.dto.employee import EmployeeDTO

class EmployeeService:
    def __init__(self, repo: EmployeeRepository, dept_repo: DepartmentRepository):
        self.repo = repo
        self.dept_repo = dept_repo

    def create_employee(self, department_id: int, full_name: str, position: str, hired_at) -> EmployeeDTO:
        EmployeeValidator.validate_department_exists(self.dept_repo, department_id)
        full_name = full_name.strip()
        position = position.strip()
        emp = self.repo.create(department_id=department_id,
                               full_name=full_name,
                               position=position,
                               hired_at=hired_at)
        return EmployeeDTO.from_orm(emp)