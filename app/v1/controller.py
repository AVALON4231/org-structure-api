from sqlalchemy.orm import Session
from app import schemas
from app.v1.services import DepartmentService
from app.v1.repositories import DepartmentRepository, EmployeeRepository
from typing import Optional

class DepartmentController:
    @staticmethod
    def create(db: Session, data: schemas.DepartmentCreate) -> schemas.DepartmentOut:
        dept_repo = DepartmentRepository(db)
        service = DepartmentService(dept_repo)
        department = service.create_department(data.name, data.parent_id)
        return schemas.DepartmentOut.from_orm(department)

    @staticmethod
    def create_employee(db: Session, department_id: int, data: schemas.EmployeeCreate) -> schemas.EmployeeOut:
        dept_repo = DepartmentRepository(db)
        emp_repo = EmployeeRepository(db)
        service = DepartmentService(dept_repo)
        employee = service.create_employee(emp_repo, department_id, data.full_name, data.position, data.hired_at)
        return schemas.EmployeeOut.from_orm(employee)

    @staticmethod
    def get(db: Session, department_id: int, depth: int, include_employees: bool) -> schemas.DepartmentDetail:
        dept_repo = DepartmentRepository(db)
        service = DepartmentService(dept_repo)
        return service.get_department_detail(department_id, depth, include_employees)

    @staticmethod
    def update(db: Session, department_id: int, data: schemas.DepartmentUpdate) -> schemas.DepartmentOut:
        dept_repo = DepartmentRepository(db)
        service = DepartmentService(dept_repo)
        dept = service.update_department(department_id, data.name, data.parent_id)
        return schemas.DepartmentOut.from_orm(dept)

    @staticmethod
    def delete(db: Session, department_id: int, mode: str, reassign_to: Optional[int]):
        dept_repo = DepartmentRepository(db)
        emp_repo = EmployeeRepository(db)
        service = DepartmentService(dept_repo)
        service.delete_department(emp_repo, department_id, mode, reassign_to)