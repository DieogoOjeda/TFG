from datetime import datetime
from pydantic import BaseModel
from app.models.reservation_model import ReservationStatus


class ReservationBase(BaseModel):
    user_id: int
    book_id: int


class ReservationCreate(ReservationBase):
    pass


class ReservationRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: ReservationStatus
    created_at: datetime
    notified_at: datetime | None = None
    expires_at: datetime | None = None

    # ✅ NUEVOS (para admin UI)
    user_email: str | None = None
    book_title: str | None = None

    class Config:
        from_attributes = True
