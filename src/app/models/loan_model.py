from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.core.database import Base
from enum import Enum as PyEnum


class LoanStatus(str, PyEnum):
    ACTIVE = "active"
    RETURNED = "returned"
    LATE = "late"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False)

    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)

    user = relationship("User", back_populates="loans")
    copy = relationship("BookCopy", back_populates="loans")
