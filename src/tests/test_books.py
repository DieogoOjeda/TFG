from tests.conftest import auth_headers

def test_list_books_public(client):
    r = client.get("/books/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_book_requires_librarian(client, student_token):
    payload = {
        "title": "Libro X",
        "authors": "Autor",
        "isbn": "9781111111111",
        "edition": "1",
        "subject": "Test",
        "access_level": "general",
        "first_copy_barcode": "BC-001",
        "first_copy_is_reference": False,
    }
    r = client.post("/books/", json=payload, headers=auth_headers(student_token))
    assert r.status_code in (401, 403)


def test_create_book_ok_librarian(client, librarian_token):
    payload = {
        "title": "Libro Test",
        "authors": "Autor Test",
        "isbn": "9782222222222",
        "edition": "1",
        "subject": "Testing",
        "access_level": "general",
        "first_copy_barcode": "BC-002",
        "first_copy_is_reference": False,
    }
    r = client.post("/books/", json=payload, headers=auth_headers(librarian_token))
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Libro Test"
    assert len(data["copies"]) == 1
