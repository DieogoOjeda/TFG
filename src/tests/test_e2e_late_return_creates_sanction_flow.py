# tests/test_e2e_late_return_creates_sanction_flow.py
from datetime import datetime, timedelta

from tests.conftest import auth_headers
from app.models.loan_model import Loan
from app.models.user_model import User

def test_e2e_late_return_creates_sanction_and_blocks_user(
    client, db_session, librarian_token, student_token, student_user
):
    # 1) Crear libro + copia
    book_payload = {
        "title": "Late Book",
        "authors": "Late Author",
        "isbn": "9785555555555",
        "edition": "1",
        "subject": "Late",
        "access_level": "general",
        "first_copy_barcode": "E2E-BC-LATE-001",
        "first_copy_is_reference": False,
    }
    r = client.post("/books/", json=book_payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201, r.text
    book = r.json()
    book_id = book["id"]
    copy_id = book["copies"][0]["id"]

    # 2) Crear préstamo
    r = client.post(
        "/loans/",
        json={"user_id": student_user.id, "copy_id": copy_id},
        headers=auth_headers(librarian_token),
    )
    assert r.status_code == 201, r.text
    loan_id = r.json()["id"]

    # 3) Forzar que el préstamo esté vencido (due_date en el pasado)
    loan = db_session.query(Loan).filter(Loan.id == loan_id).first()
    assert loan is not None
    loan.due_date = datetime.utcnow() - timedelta(days=3)
    db_session.commit()

    # 4) Devolver -> debe marcar LATE y crear sanción + bloquear usuario :contentReference[oaicite:10]{index=10}
    r = client.post(f"/loans/{loan_id}/return")
    assert r.status_code == 201, r.text
    loan_after = r.json()
    assert loan_after["status"] == "LATE"

    # 5) Comprobar que el usuario quedó bloqueado
    u = db_session.query(User).filter(User.id == student_user.id).first()
    assert u is not None
    assert u.blocked_until is not None
    assert u.blocked_until > datetime.utcnow()

    # 6) Comprobar que existe al menos una sanción para ese usuario (admin)
    r = client.get(
        f"/sanctions/?email={student_user.email}",
        headers=auth_headers(librarian_token),
    )
    assert r.status_code == 200, r.text
    sanctions = r.json()
    assert len(sanctions) >= 1
    # (opcional) comprobar que alguna sanción corresponde al libro
    assert any(s.get("book_id") == book_id for s in sanctions)
