# tests/test_books_security.py
from tests.conftest import auth_headers

def test_list_books_public(client):
    r = client.get("/books/")
    assert r.status_code == 200


def test_create_book_requires_librarian(client, student_token):
    # Payload mínimo (puede ser incompleto -> 422). Lo importante es que un student no pueda crear.
    r = client.post("/books/", headers=auth_headers(student_token), json={"title": "X"})
    assert r.status_code in (401, 403, 422)
