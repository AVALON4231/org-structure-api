from typing import Optional
from app.repositories.department_repo import DepartmentRepository
from app.validators.department_validator import DepartmentValidator
from app.dto.department import DepartmentDTO, DepartmentDetailDTO
from app.dto.employee import EmployeeDTO
from app import models

class DepartmentService:
    def __init__(self, repo: DepartmentRepository):
        self.repo = repo

    def create_department(self, name: str, parent_id: Optional[int]) -> DepartmentDTO:
        name = name.strip()
        if parent_id is not None:
            DepartmentValidator.validate_parent_exists(self.repo, parent_id)
        DepartmentValidator.validate_name_unique(self.repo, name, parent_id)
        dept = self.repo.create(name=name, parent_id=parent_id)
        return DepartmentDTO.from_orm(dept)

    def get_department_detail(self, department_id: int, depth: int, include_employees: bool) -> DepartmentDetailDTO:
        dept = self.repo.get_or_404(department_id)
        dept = self.repo.get_with_children(department_id)
        return self._build_tree(dept, depth, include_employees)

    def _build_tree(self, dept: models.Department, depth: int, include_employees: bool) -> DepartmentDetailDTO:
        employees_dto = []
        if include_employees:
            employees_dto = [EmployeeDTO.from_orm(e) for e in sorted(dept.employees, key=lambda e: e.created_at)]
        children_dto = []
        if depth > 0:
            for child in dept.children:
                children_dto.append(self._build_tree(child, depth - 1, include_employees))
        return DepartmentDetailDTO(
            department=DepartmentDTO.from_orm(dept),
            employees=employees_dto,
            children=children_dto
        )

    def update_department(self, department_id: int, name: Optional[str], parent_id: Optional[int]) -> DepartmentDTO:
        dept = self.repo.get_or_404(department_id)

        if name is not None:
            name = name.strip()
            target_parent_id = parent_id if parent_id is not None else dept.parent_id
            DepartmentValidator.validate_name_unique(self.repo, name, target_parent_id, exclude_id=department_id)
            dept.name = name

        if parent_id is not None:
            DepartmentValidator.validate_not_self_parent(department_id, parent_id)
            DepartmentValidator.validate_parent_exists(self.repo, parent_id)
            DepartmentValidator.validate_no_cycle(self.repo, department_id, parent_id)
            dept.parent_id = parent_id

        self.repo.save(dept)
        return DepartmentDTO.from_orm(dept)

    def delete_department(self, department_id: int, mode: str, reassign_to: Optional[int]):
        dept = self.repo.get_or_404(department_id)
        if mode == "cascade":
            self.repo.delete(dept)
        elif mode == "reassign":
            if not reassign_to:
                raise HTTPException(status_code=400, detail="reassign_to_department_id is required for mode=reassign")
            # Проверим существование целевого отдела
            self.repo.get_or_404(reassign_to)
            # Получим сотрудников и переместим их
            # Нужен EmployeeRepository, чтобы избежать пересечения ответственности
            # Для краткости используем прямой доступ, но в реальном проекте лучше передавать сервис сотрудников
            from app.repositories.employee_repo import EmployeeRepository
            emp_repo = EmployeeRepository(self.repo.db)
            employees = emp_repo.get_by_department(department_id)
            for emp in employees:
                emp.department_id = reassign_to
                emp_repo.save(emp)
            self.repo.delete(dept)
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")