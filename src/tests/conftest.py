# tests/conftest.py
import os
import sys
import uuid
import pytest
from datetime import datetime, timedelta

# ✅ Añadir /src al PYTHONPATH ANTES de importar "app"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.main import app
from app.dependencies import get_db as app_get_db
from app.utils import security as security_module

from app.models.user_model import User, UserRole
from app.models.book_model import Book, BookCopy, AccessLevel, CopyStatus
from app.models.loan_model import Loan, LoanStatus
from app.models.reservation_model import Reservation, ReservationStatus
from app.models.sanction_model import Sanction


# ✅ SQLite en memoria, estable en Windows + TestClient
engine_test = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db_session():
    """
    Transacción por test:
    - empieza transacción
    - yield session
    - rollback al final
    => BD limpia en cada test (evita UNIQUE constraint)
    """
    connection = engine_test.connect()
    trans = connection.begin()
    session = SessionTesting(bind=connection)

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    # Override del get_db que usan routers
    def override_get_db():
        yield db_session

    # Override del get_db que usa auth/security (en auth_router se usa app.utils.security.get_db) :contentReference[oaicite:1]{index=1}
    def override_security_get_db():
        yield db_session

    app.dependency_overrides[app_get_db] = override_get_db
    app.dependency_overrides[security_module.get_db] = override_security_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- Factories ----------
@pytest.fixture()
def librarian_user(db_session):
    u = User(
        external_id=f"LIB-{uuid.uuid4()}",
        email="librarian@example.com",
        full_name="Lib Rarian",
        role=UserRole.LIBRARIAN,
        is_active=True,
        password_hash=security_module.get_password_hash("pass123456"),
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def student_user(db_session):
    u = User(
        external_id=f"STU-{uuid.uuid4()}",
        email="student@example.com",
        full_name="Stu Dent",
        role=UserRole.STUDENT,
        is_active=True,
        password_hash=security_module.get_password_hash("pass123456"),
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def librarian_token(client, librarian_user):
    r = client.post("/auth/login", json={"email": librarian_user.email, "password": "pass123456"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def student_token(client, student_user):
    r = client.post("/auth/login", json={"email": student_user.email, "password": "pass123456"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def book_with_copy(db_session):
    b = Book(
        title="Test Book",
        authors="Author One",
        isbn="9780000000000",
        edition="1",
        subject="Testing",
        access_level=AccessLevel.GENERAL,
    )
    db_session.add(b)
    db_session.commit()
    db_session.refresh(b)

    c = BookCopy(
        book_id=b.id,
        barcode=f"BC-{uuid.uuid4()}",
        is_reference=False,
        status=CopyStatus.AVAILABLE,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return b, c


@pytest.fixture()
def active_loan(db_session, student_user, book_with_copy):
    _, c = book_with_copy
    loan = Loan(
        user_id=student_user.id,
        copy_id=c.id,
        due_date=datetime.utcnow() + timedelta(days=7),
        status=LoanStatus.ACTIVE,
    )
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    c.status = CopyStatus.LOANED
    db_session.commit()
    return loan


@pytest.fixture()
def active_reservation(db_session, student_user, book_with_copy):
    b, _ = book_with_copy
    r = Reservation(user_id=student_user.id, book_id=b.id, status=ReservationStatus.ACTIVE)
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return r


@pytest.fixture()
def sanction(db_session, student_user, book_with_copy):
    b, c = book_with_copy
    s = Sanction(user_id=student_user.id, book_id=b.id, copy_id=c.id, days=7)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s
