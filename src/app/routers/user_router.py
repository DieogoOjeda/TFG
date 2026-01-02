from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate, UserRead
from app.utils.security import get_password_hash, get_current_user, require_roles
from app.services.user_service import get_user_by_email

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(
        external_id=user_in.external_id,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Si no es bibliotecario, solo se puede ver a sí mismo
    if current_user.role != UserRole.LIBRARIAN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este usuario.")

    return user

@router.get("/by-email/{email}", response_model=UserRead)
def get_user_by_email_endpoint(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.LIBRARIAN)),
):
    """
    Devuelve un usuario a partir de su email.
    Solo accesible para bibliotecarios.
    """
    return get_user_by_email(db, email)


@router.put("/{user_id}", response_model=UserRead, )
def update_user(user_id: int, user_in: UserCreate, db: Session = Depends    (get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    for key, value in user_in.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente."}