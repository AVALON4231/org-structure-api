from fastapi import HTTPException
from app.repositories.department_repo import DepartmentRepository

class EmployeeValidator:
    @staticmethod
    def validate_department_exists(repo: DepartmentRepository, department_id: int):
        repo.get_or_404(department_id)  # 404, если отдела нет