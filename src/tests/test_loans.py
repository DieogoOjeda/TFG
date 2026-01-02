from tests.conftest import auth_headers

def test_create_loan_ok(client, librarian_token, student_user, book_with_copy):
    _, copy = book_with_copy
    payload = {"user_id": student_user.id, "copy_id": copy.id}
    r = client.post("/loans/", json=payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201
    assert r.json()["status"] == "active"


def test_create_loan_copy_already_loaned(client, librarian_token, student_user, active_loan):
    payload = {"user_id": student_user.id, "copy_id": active_loan.copy_id}
    r = client.post("/loans/", json=payload, headers=auth_headers(librarian_token))
    assert r.status_code == 409


def test_list_loans_requires_librarian(client, student_token):
    r = client.get("/loans/", headers=auth_headers(student_token))
    assert r.status_code in (401, 403)


def test_list_loans_ok_librarian(client, librarian_token, active_loan):
    r = client.get("/loans/", headers=auth_headers(librarian_token))
    assert r.status_code == 200
    assert len(r.json()) >= 1
