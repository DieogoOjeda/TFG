from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

from sqlalchemy.ext.hybrid import hybrid_property


class ReservationStatus(str, enum.Enum):
    ACTIVE = "active"          # En cola esperando ejemplar
    NOTIFIED = "notified"      # Ejemplar disponible para recogida
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FULFILLED = "fulfilled"    # Se transformó en préstamo


class Reservation(Base):
    """
    Reserva por título (cola FIFO) (UC-06, RB-06)
    """
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    status = Column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # ventana de recogida

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")
    
    @hybrid_property
    def user_email(self):
        return self.user.email if self.user else None

    @hybrid_property
    def book_title(self):
        return self.book.title if self.book else None
