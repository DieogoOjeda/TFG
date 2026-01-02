from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.sanction_schema import SanctionRead, SanctionCreate
from app.services.sanction_service import create_sanction
from app.services.sanction_service import (
    list_sanctions_by_user,
    list_sanctions,
    list_sanctions_by_user_email,
)
from app.utils.security import require_roles
from app.models.user_model import UserRole

router = APIRouter()

@router.post(
    "/", 
    response_model=SanctionRead, 
    status_code=status.HTTP_201_CREATED
)
def create_sanction_endpoint(
    sanction_in: SanctionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),  # 👈 solo admin
):
    return create_sanction(db, sanction_in)


@router.get("/", response_model=list[SanctionRead])
def list_sanctions_endpoint(
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    if email:
        return list_sanctions_by_user_email(db, email)
    return list_sanctions(db)


@router.get("/user/{user_id}", response_model=list[SanctionRead])
def list_user_sanctions_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    return list_sanctions_by_user(db, user_id)
