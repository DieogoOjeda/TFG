from datetime import datetime
from pydantic import BaseModel



class SanctionBase(BaseModel):
    user_id: int
    days: int

    # Nuevo: sanción por ejemplar concreto
    copy_id: int

    # Opcional: si quieres guardar también el libro
    book_id: int | None = None


class SanctionCreate(SanctionBase):
    pass


class SanctionRead(BaseModel):
    id: int
    created_at: datetime
    days: int
    user_id: int
    book_id: int | None = None

    user_email: str | None = None
    user_name: str | None = None

    class Config:
        from_attributes = True
