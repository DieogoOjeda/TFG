from datetime import datetime
from pydantic import BaseModel
from app.models.loan_model import LoanStatus


class LoanCreate(BaseModel):
    user_id: int
    copy_id: int


class LoanUser(BaseModel):
    id: int
    email: str
    full_name: str | None = None

    class Config:
        from_attributes = True


class LoanBook(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class LoanCopy(BaseModel):
    id: int
    barcode: str
    book: LoanBook

    class Config:
        from_attributes = True


class LoanRead(BaseModel):
    id: int
    user_id: int
    copy_id: int
    loan_date: datetime
    due_date: datetime
    return_date: datetime | None
    status: LoanStatus

    user: LoanUser
    copy: LoanCopy

    class Config:
        from_attributes = True