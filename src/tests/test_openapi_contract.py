# tests/test_openapi_contract.py
def test_openapi_has_expected_prefixes(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})

    # Auth
    assert "/auth/login" in paths
    assert "/auth/me" in paths

    # Core prefixes
    assert any(p.startswith("/users") for p in paths)
    assert any(p.startswith("/books") for p in paths)
    assert any(p.startswith("/loans") for p in paths)
    assert any(p.startswith("/reservations") for p in paths)
    assert any(p.startswith("/sanctions") for p in paths)

    # Anti-regression: evitar dobles prefijos
    assert not any(p.startswith("/sanctions/sanctions") for p in paths)
