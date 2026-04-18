def test_login_page_loads(client):
    r = client.get("/admin/login")
    assert r.status_code == 200
    assert b"Sign In" in r.data or b"Sign in" in r.data or b"login" in r.data.lower()


def test_login_with_valid_credentials(client):
    r = client.post("/admin/login", data={"username": "testadmin", "password": "testpass"}, follow_redirects=True)
    assert r.status_code == 200


def test_login_with_invalid_credentials(client):
    r = client.post("/admin/login", data={"username": "wrong", "password": "wrong"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Invalid" in r.data or b"invalid" in r.data or b"error" in r.data.lower()


def test_dashboard_requires_auth(client):
    r = client.get("/admin/dashboard")
    assert r.status_code == 302  # Redirect to login


def test_api_requires_auth(client):
    r = client.get("/api/contacts")
    assert r.status_code in [302, 401]


def test_logout(auth_client):
    r = auth_client.get("/admin/logout", follow_redirects=True)
    assert r.status_code == 200
    # After logout, dashboard should redirect
    r2 = auth_client.get("/admin/dashboard")
    assert r2.status_code == 302
