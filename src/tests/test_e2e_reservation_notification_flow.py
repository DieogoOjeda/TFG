# tests/test_e2e_reservation_notification_flow.py
from tests.conftest import auth_headers

def test_e2e_reservation_then_return_notifies_and_reserves_copy(
    client, librarian_token, student_token, student_user
):
    # 1) Crear libro + 1 copia (admin)
    book_payload = {
        "title": "Reserva Book",
        "authors": "Reserva Author",
        "isbn": "9784444444444",
        "edition": "1",
        "subject": "Reservas",
        "access_level": "general",
        "first_copy_barcode": "E2E-BC-RES-001",
        "first_copy_is_reference": False,
    }
    r = client.post("/books/", json=book_payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201, r.text
    book = r.json()
    book_id = book["id"]
    copy_id = book["copies"][0]["id"]

    # 2) Prestar la única copia (admin) -> deja el libro sin copias disponibles
    r = client.post(
        "/loans/",
        json={"user_id": student_user.id, "copy_id": copy_id},
        headers=auth_headers(librarian_token),
    )
    assert r.status_code == 201, r.text
    loan_id = r.json()["id"]

    # 3) Crear reserva (student) -> debe permitir solo si TODAS las copias están prestadas :contentReference[oaicite:5]{index=5}
    r = client.post(
        "/reservations/",
        json={"user_id": student_user.id, "book_id": book_id},
        headers=auth_headers(student_token),
    )
    assert r.status_code == 201, r.text  # reservation_router create: status_code=201 :contentReference[oaicite:6]{index=6}
    reservation = r.json()
    assert reservation["status"] == "ACTIVE"
    reservation_id = reservation["id"]

    # 4) Devolver el préstamo -> debe NOTIFY la reserva y poner la copia RESERVED :contentReference[oaicite:7]{index=7}
    r = client.post(f"/loans/{loan_id}/return")
    assert r.status_code == 201, r.text

    # 5) Comprobar que la reserva pasa a NOTIFIED consultando list_user_reservations
    r = client.get(f"/reservations/user/{student_user.id}", headers=auth_headers(student_token))
    assert r.status_code == 200, r.text
    reservations = r.json()
    rsv = next(x for x in reservations if x["id"] == reservation_id)
    assert rsv["status"] == "NOTIFIED"

    # 6) Comprobar que la copia está RESERVED
    r = client.get(f"/books/{book_id}")
    assert r.status_code == 200, r.text
    assert r.json()["copies"][0]["status"] == "RESERVED"
