from app import models

class EmployeeRepository:
    def __init__(self, db):
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