from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from fastapi import HTTPException
from app import models

class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_404(self, department_id: int) -> models.Department:
        dept = self.db.query(models.Department).filter(models.Department.id == department_id).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        return dept

    def find_by_name_and_parent(self, name: str, parent_id: int):
        return self.db.query(models.Department).filter(
            and_(models.Department.name == name, models.Department.parent_id == parent_id)
        ).first()

    def create(self, name: str, parent_id: int) -> models.Department:
        dept = models.Department(name=name, parent_id=parent_id)
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def save(self, dept: models.Department):
        self.db.commit()
        self.db.refresh(dept)

    def get_with_children(self, department_id: int) -> models.Department:
        # Загружаем сотрудников и детей, чтобы избежать N+1 при построении дерева
        return self.db.query(models.Department).options(
            joinedload(models.Department.employees),
            joinedload(models.Department.children).joinedload(models.Department.children)
        ).filter(models.Department.id == department_id).first()

    def is_descendant(self, ancestor_id: int, possible_descendant_id: int) -> bool:
        # Проверяет, является ли possible_descendant_id потомком ancestor_id
        from sqlalchemy import func
        cte = self.db.query(
            models.Department.id
        ).filter(models.Department.parent_id == ancestor_id).cte(name="descendants", recursive=True)
        cte = cte.union_all(
            self.db.query(models.Department.id).filter(models.Department.parent_id == cte.c.id)
        )
        result = self.db.query(cte).filter(cte.c.id == possible_descendant_id).first()
        return result is not None

    def delete(self, dept: models.Department):
        self.db.delete(dept)
        self.db.commit()


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, department_id: int, full_name: str, position: str, hired_at) -> models.Employee:
        emp = models.Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at
        )
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def get_by_department(self, department_id: int):
        return self.db.query(models.Employee).filter(
            models.Employee.department_id == department_id
        ).all()

    def save(self, emp: models.Employee):
        self.db.commit()
        self.db.refresh(emp)