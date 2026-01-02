# tests/test_e2e_loan_flow.py
from tests.conftest import auth_headers

def test_e2e_loan_create_and_return_updates_copy_status(client, librarian_token, student_user):
    # 1) Crear libro + 1 copia (admin)
    book_payload = {
        "title": "E2E Book",
        "authors": "E2E Author",
        "isbn": "9783333333333",
        "edition": "1",
        "subject": "E2E",
        "access_level": "general",
        "first_copy_barcode": "E2E-BC-001",
        "first_copy_is_reference": False,
    }
    r = client.post("/books/", json=book_payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201, r.text  # book_router: status_code=201 :contentReference[oaicite:1]{index=1}
    book = r.json()
    book_id = book["id"]
    copy_id = book["copies"][0]["id"]

    # 2) Crear préstamo (admin)
    loan_payload = {"user_id": student_user.id, "copy_id": copy_id}
    r = client.post("/loans/", json=loan_payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201, r.text  # loan_router create: status_code=201 :contentReference[oaicite:2]{index=2}
    loan = r.json()
    loan_id = loan["id"]
    assert loan["status"] == "ACTIVE"

    # 3) Verificar que la copia está LOANED (consultando el libro)
    r = client.get(f"/books/{book_id}")
    assert r.status_code == 200, r.text
    book_after_loan = r.json()
    assert book_after_loan["copies"][0]["status"] == "LOANED"

    # 4) Devolver préstamo (tu endpoint devuelve 201 actualmente) :contentReference[oaicite:3]{index=3}
    r = client.post(f"/loans/{loan_id}/return")
    assert r.status_code == 201, r.text
    loan_after_return = r.json()
    assert loan_after_return["status"] in ("RETURNED", "LATE")

    # 5) Comprobar que la copia vuelve a AVAILABLE o RESERVED (si hubiese reserva)
    r = client.get(f"/books/{book_id}")
    assert r.status_code == 200, r.text
    book_after_return = r.json()
    assert book_after_return["copies"][0]["status"] in ("AVAILABLE", "RESERVED")
