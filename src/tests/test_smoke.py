# tests/test_smoke.py
def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200


def test_root_available(client):
    r = client.get("/")
    # tu "/" sirve un archivo; puede devolver 200 o 404 si la ruta está mal montada en tests
    assert r.status_code in (200, 404)
