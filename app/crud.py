from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from fastapi import HTTPException, status
from app import models, schemas
from typing import List, Optional

def get_department(db: Session, department_id: int) -> models.Department:
    dept = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

def create_department(db: Session, data: schemas.DepartmentCreate) -> models.Department:
    # Проверка уникальности имени в пределах родителя
    if data.parent_id:
        parent = get_department(db, data.parent_id)
    existing = db.query(models.Department).filter(
        and_(models.Department.name == data.name, models.Department.parent_id == data.parent_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department with this name already exists under the same parent")

    dept = models.Department(**data.dict())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def create_employee(db: Session, department_id: int, data: schemas.EmployeeCreate) -> models.Employee:
    get_department(db, department_id)  # проверка существования
    emp = models.Employee(**data.dict(), department_id=department_id)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

def get_descendant_ids(db: Session, dept_id: int) -> set:
    """Рекурсивный сбор всех ID потомков (включая сам dept_id)"""
    ids = {dept_id}
    children = db.query(models.Department).filter(models.Department.parent_id == dept_id).all()
    for child in children:
        ids.update(get_descendant_ids(db, child.id))
    return ids

def update_department(db: Session, department_id: int, data: schemas.DepartmentUpdate) -> models.Department:
    dept = get_department(db, department_id)

    if data.name is not None:
        # Уникальность имени
        existing = db.query(models.Department).filter(
            and_(
                models.Department.name == data.name,
                models.Department.parent_id == data.parent_id if data.parent_id is not None else dept.parent_id,
                models.Department.id != department_id
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Name already exists in target parent")
        dept.name = data.name

    if data.parent_id is not None:
        if data.parent_id == department_id:
            raise HTTPException(status_code=400, detail="Cannot set parent to itself")
        # Проверка на цикл: новый родитель не должен быть потомком текущего отдела
        new_parent = get_department(db, data.parent_id)
        descendant_ids = get_descendant_ids(db, department_id)
        if data.parent_id in descendant_ids:
            raise HTTPException(status_code=409, detail="Cannot move department into its own subtree")
        dept.parent_id = data.parent_id

    db.commit()
    db.refresh(dept)
    return dept

def delete_department(db: Session, department_id: int, mode: str, reassign_to: Optional[int] = None):
    dept = get_department(db, department_id)
    if mode == "cascade":
        db.delete(dept)  # каскад благодаря настройкам отношений
        db.commit()
    elif mode == "reassign":
        if not reassign_to:
            raise HTTPException(status_code=400, detail="reassign_to_department_id is required for mode=reassign")
        target = get_department(db, reassign_to)
        # Перемещаем сотрудников
        employees = db.query(models.Employee).filter(models.Employee.department_id == department_id).all()
        for emp in employees:
            emp.department_id = reassign_to
        # Дочерние подразделения удаляем каскадно
        # Можно просто удалить текущий отдел, предварительно переместив сотрудников
        db.delete(dept)  # дочерние удалятся каскадом, сотрудники уже переведены
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'cascade' or 'reassign'")

def build_department_tree(db: Session, dept: models.Department, depth: int, include_employees: bool) -> schemas.DepartmentDetail:
    # Загружаем сотрудников если нужно
    employees = []
    if include_employees:
        employees = sorted(dept.employees, key=lambda e: e.created_at or "")
    children = []
    if depth > 0:
        for child in dept.children:
            children.append(build_department_tree(db, child, depth - 1, include_employees))
    return schemas.DepartmentDetail(
        department=schemas.DepartmentOut.from_orm(dept),
        employees=[schemas.EmployeeOut.from_orm(e) for e in employees],
        children=children
    )

def get_department_detail(db: Session, department_id: int, depth: int = 1, include_employees: bool = True):
    dept = get_department(db, department_id)
    # Явная подгрузка детей (чтобы не было N+1)
    dept = db.query(models.Department).options(
        joinedload(models.Department.children).joinedload(models.Department.children),  # можно рекурсивно до нужной глубины, но для простоты загрузим все
        joinedload(models.Department.employees)
    ).filter(models.Department.id == department_id).first()
    return build_department_tree(db, dept, depth, include_employees)