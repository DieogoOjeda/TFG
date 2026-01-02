from tests.conftest import auth_headers

def test_create_reservation_fails_if_copy_available(
    client, student_token, student_user, book_with_copy
):
    book, _ = book_with_copy
    payload = {"user_id": student_user.id, "book_id": book.id}
    r = client.post("/reservations/", json=payload, headers=auth_headers(student_token))
    assert r.status_code == 409


def test_create_reservation_ok_when_all_copies_loaned(
    client, student_token, student_user, active_loan
):
    book_id = active_loan.copy.book_id
    payload = {"user_id": student_user.id, "book_id": book_id}
    r = client.post("/reservations/", json=payload, headers=auth_headers(student_token))
    assert r.status_code == 201
    assert r.json()["status"] == "active"


def test_list_reservations_admin(client, librarian_token, active_reservation):
    r = client.get("/reservations/", headers=auth_headers(librarian_token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_cancel_reservation(client, student_token, active_reservation):
    r = client.post(
        f"/reservations/{active_reservation.id}/cancel",
        headers=auth_headers(student_token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"
