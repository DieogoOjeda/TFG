# src/app/models/__init__.py

from app.core.database import Base  # por si lo necesitas en otros sitios

# Importa TODOS los modelos para que SQLAlchemy los registre en Base.metadata
from .user_model import User
from .book_model import Book, BookCopy
from .loan_model import Loan
from .reservation_model import Reservation
from .sanction_model import Sanction