from tests.conftest import auth_headers

def test_create_sanction_requires_librarian(client, student_token, active_loan):
    payload = {
        "user_id": active_loan.user_id,
        "copy_id": active_loan.copy_id,
        "book_id": active_loan.copy.book_id,
        "days": 7,
    }
    r = client.post("/sanctions/", json=payload, headers=auth_headers(student_token))
    assert r.status_code in (401, 403)


def test_create_sanction_ok(client, librarian_token, active_loan):
    payload = {
        "user_id": active_loan.user_id,
        "copy_id": active_loan.copy_id,
        "book_id": active_loan.copy.book_id,
        "days": 7,
    }
    r = client.post("/sanctions/", json=payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201
    data = r.json()
    assert data["days"] == 7
    assert data["user_email"] is not None
    assert data["user_name"] is not None


def test_list_sanctions_filter_by_email(
    client, librarian_token, sanction, student_user
):
    r = client.get(
        f"/sanctions/?email={student_user.email}",
        headers=auth_headers(librarian_token),
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1
