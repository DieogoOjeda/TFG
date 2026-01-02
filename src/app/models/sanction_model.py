from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.ext.hybrid import hybrid_property


class Sanction(Base):
    """
    Sanción aplicada a un usuario por un préstamo atrasado.

    Campos:
    - created_at: día de creación de la sanción
    - days: días de sanción (bloqueo)
    - user_id: usuario sancionado
    - book_id: libro que NO se devolvió a tiempo
    """
    __tablename__ = "sanctions"


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    # 👇 nuevo
    copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    days = Column(Integer, nullable=False)

    user = relationship("User", back_populates="sanctions")
    book = relationship("Book")
    copy = relationship("BookCopy")

    @hybrid_property
    def user_email(self):
        return self.user.email if self.user else None
    
    @hybrid_property
    def user_name(self):
        return self.user.full_name if self.user else None
