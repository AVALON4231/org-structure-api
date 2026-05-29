from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas
from app.v1.repositories import DepartmentRepository, EmployeeRepository

class DepartmentService:
    def __init__(self, repo: DepartmentRepository):
        self.repo = repo

    def create_department(self, name: str, parent_id: Optional[int]) -> models.Department:
        name = name.strip()
        if parent_id:
            # Проверяем, что родитель существует (репозиторий выбросит 404)
            self.repo.get_or_404(parent_id)
        # Проверка уникальности имени в родителе
        existing = self.repo.find_by_name_and_parent(name, parent_id)
        if existing:
            raise HTTPException(status_code=400, detail="Department with this name already exists under the same parent")
        return self.repo.create(name=name, parent_id=parent_id)

    def create_employee(self, emp_repo: EmployeeRepository, department_id: int,
                        full_name: str, position: str, hired_at) -> models.Employee:
        self.repo.get_or_404(department_id)  # проверка существования отдела
        full_name = full_name.strip()
        position = position.strip()
        return emp_repo.create(department_id=department_id,
                               full_name=full_name,
                               position=position,
                               hired_at=hired_at)

    def get_department_detail(self, department_id: int, depth: int, include_employees: bool) -> schemas.DepartmentDetail:
        dept = self.repo.get_or_404(department_id)
        # Явная подгрузка детей и сотрудников для построения дерева
        dept = self.repo.get_with_children(department_id)
        return self._build_tree(dept, depth, include_employees)

    def _build_tree(self, dept: models.Department, depth: int, include_employees: bool) -> schemas.DepartmentDetail:
        employees = []
        if include_employees:
            employees = sorted(dept.employees, key=lambda e: e.created_at or "")
        children = []
        if depth > 0:
            for child in dept.children:
                children.append(self._build_tree(child, depth - 1, include_employees))
        return schemas.DepartmentDetail(
            department=schemas.DepartmentOut.from_orm(dept),
            employees=[schemas.EmployeeOut.from_orm(e) for e in employees],
            children=children
        )

    def update_department(self, department_id: int, name: Optional[str], parent_id: Optional[int]) -> models.Department:
        dept = self.repo.get_or_404(department_id)

        if name is not None:
            name = name.strip()
            # Уникальность имени в контексте нового родителя (или текущего, если parent_id не меняется)
            target_parent_id = parent_id if parent_id is not None else dept.parent_id
            existing = self.repo.find_by_name_and_parent(name, target_parent_id)
            if existing and existing.id != department_id:
                raise HTTPException(status_code=400, detail="Name already exists in target parent")
            dept.name = name

        if parent_id is not None:
            if parent_id == department_id:
                raise HTTPException(status_code=400, detail="Cannot set parent to itself")
            # Проверка на цикл: новый родитель не должен быть потомком текущего отдела
            if self.repo.is_descendant(department_id, parent_id):
                raise HTTPException(status_code=409, detail="Cannot move department into its own subtree")
            # Проверяем, что новый родитель существует
            self.repo.get_or_404(parent_id)
            dept.parent_id = parent_id

        self.repo.save(dept)
        return dept

    def delete_department(self, emp_repo: EmployeeRepository, department_id: int, mode: str, reassign_to: Optional[int]):
        dept = self.repo.get_or_404(department_id)
        if mode == "cascade":
            self.repo.delete(dept)
        elif mode == "reassign":
            if not reassign_to:
                raise HTTPException(status_code=400, detail="reassign_to_department_id is required for mode=reassign")
            target_dept = self.repo.get_or_404(reassign_to)
            # Переводим всех сотрудников удаляемого отдела в целевой
            employees = emp_repo.get_by_department(department_id)
            for emp in employees:
                emp.department_id = reassign_to
                emp_repo.save(emp)
            # Удаляем отдел (дочерние удалятся каскадно)
            self.repo.delete(dept)