from tests.conftest import auth_headers

def test_create_user_ok(client):
    payload = {
        "external_id": "EXT-999",
        "email": "new@test.com",
        "full_name": "New User",
        "role": "student",
        "password": "pass123456",
    }
    r = client.post("/users/", json=payload)
    assert r.status_code == 201
    assert r.json()["email"] == payload["email"]


def test_get_user_self_ok(client, student_token, student_user):
    r = client.get(f"/users/{student_user.id}", headers=auth_headers(student_token))
    assert r.status_code == 200


def test_get_user_other_forbidden(client, student_token, librarian_user):
    r = client.get(f"/users/{librarian_user.id}", headers=auth_headers(student_token))
    assert r.status_code == 403
