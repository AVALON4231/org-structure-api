from sqlalchemy.orm import Session
from app.services.department_service import DepartmentService
from app.repositories.department_repo import DepartmentRepository
from app.api import schemas
from typing import Optional

class DepartmentController:
    @staticmethod
    def create(db: Session, data: schemas.DepartmentCreateRequest) -> schemas.DepartmentOut:
        repo = DepartmentRepository(db)
        service = DepartmentService(repo)
        dto = service.create_department(data.name, data.parent_id)
        return schemas.DepartmentOut.from_orm(dto)

    @staticmethod
    def get(db: Session, department_id: int, depth: int, include_employees: bool) -> schemas.DepartmentDetailOut:
        repo = DepartmentRepository(db)
        service = DepartmentService(repo)
        detail_dto = service.get_department_detail(department_id, depth, include_employees)
        # Рекурсивное преобразование в схему ответа (можно сделать через from_orm, если поля совпадают)
        # Так как структуры DTO и схемы идентичны, можно просто сериализовать
        return _map_detail_dto_to_out(detail_dto)

    @staticmethod
    def update(db: Session, department_id: int, data: schemas.DepartmentUpdateRequest) -> schemas.DepartmentOut:
        repo = DepartmentRepository(db)
        service = DepartmentService(repo)
        dto = service.update_department(department_id, data.name, data.parent_id)
        return schemas.DepartmentOut.from_orm(dto)

    @staticmethod
    def delete(db: Session, department_id: int, mode: str, reassign_to: Optional[int]):
        repo = DepartmentRepository(db)
        service = DepartmentService(repo)
        service.delete_department(department_id, mode, reassign_to)

def _map_detail_dto_to_out(dto):
    # Простой рекурсивный маппинг, можно использовать pydantic parse_obj
    return schemas.DepartmentDetailOut(
        department=schemas.DepartmentOut.from_orm(dto.department),
        employees=[schemas.EmployeeOut.from_orm(e) for e in dto.employees],
        children=[_map_detail_dto_to_out(c) for c in dto.children]
    )