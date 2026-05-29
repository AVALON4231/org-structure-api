from fastapi import HTTPException, status
from app.repositories.department_repo import DepartmentRepository

class DepartmentValidator:
    @staticmethod
    def validate_name_unique(repo: DepartmentRepository, name: str, parent_id: int, exclude_id: int = None):
        existing = repo.find_by_name_and_parent(name, parent_id)
        if existing and (exclude_id is None or existing.id != exclude_id):
            raise HTTPException(
                status_code=400,
                detail="Department with this name already exists under the same parent"
            )

    @staticmethod
    def validate_not_self_parent(department_id: int, parent_id: int):
        if department_id == parent_id:
            raise HTTPException(status_code=400, detail="Cannot set parent to itself")

    @staticmethod
    def validate_no_cycle(repo: DepartmentRepository, department_id: int, new_parent_id: int):
        if repo.is_descendant(department_id, new_parent_id):
            raise HTTPException(status_code=409, detail="Cannot move department into its own subtree")

    @staticmethod
    def validate_parent_exists(repo: DepartmentRepository, parent_id: int):
        repo.get_or_404(parent_id)  # вызовет 404, если нет