import json


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


# --- Contacts ---

def test_create_contact(auth_client):
    r = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Test User", "email": "test@example.com", "status": "Lead"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["name"] == "Test User"
    assert r.json["email"] == "test@example.com"
    assert r.json["id"] is not None


def test_create_contact_requires_name(auth_client):
    r = auth_client.post("/api/contacts",
        data=json.dumps({"email": "no-name@example.com"}),
        content_type="application/json")
    assert r.status_code == 400


def test_list_contacts(auth_client):
    # Create one first
    auth_client.post("/api/contacts",
        data=json.dumps({"name": "List Test"}),
        content_type="application/json")
    r = auth_client.get("/api/contacts")
    assert r.status_code == 200
    assert isinstance(r.json, list)
    assert len(r.json) >= 1


def test_search_contacts(auth_client):
    auth_client.post("/api/contacts",
        data=json.dumps({"name": "Searchable Person", "email": "search@test.com"}),
        content_type="application/json")
    r = auth_client.get("/api/contacts?q=Searchable")
    assert r.status_code == 200
    assert any(c["name"] == "Searchable Person" for c in r.json)


def test_get_single_contact(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Get Me"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.get(f"/api/contacts/{cid}")
    assert r.status_code == 200
    assert r.json["name"] == "Get Me"
    assert "notes" in r.json
    assert "deals" in r.json


def test_update_contact(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Update Me"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.put(f"/api/contacts/{cid}",
        data=json.dumps({"name": "Updated Name", "status": "Customer"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["name"] == "Updated Name"
    assert r.json["status"] == "Customer"


def test_delete_contact(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Delete Me"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.delete(f"/api/contacts/{cid}")
    assert r.status_code == 200
    # Verify deleted
    r2 = auth_client.get(f"/api/contacts/{cid}")
    assert r2.status_code == 404


# --- Notes ---

def test_create_note(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Note Contact"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.post(f"/api/contacts/{cid}/notes",
        data=json.dumps({"content": "This is a test note"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["content"] == "This is a test note"


def test_list_notes(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Notes Contact"}),
        content_type="application/json")
    cid = cr.json["id"]
    auth_client.post(f"/api/contacts/{cid}/notes",
        data=json.dumps({"content": "Note 1"}),
        content_type="application/json")
    r = auth_client.get(f"/api/contacts/{cid}/notes")
    assert r.status_code == 200
    assert len(r.json) >= 1


# --- Deals ---

def test_create_deal(auth_client):
    r = auth_client.post("/api/deals",
        data=json.dumps({"title": "Test Deal", "value": 50000, "stage": "New Lead"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["title"] == "Test Deal"
    assert r.json["value"] == 50000.0


def test_create_deal_requires_title(auth_client):
    r = auth_client.post("/api/deals",
        data=json.dumps({"value": 1000}),
        content_type="application/json")
    assert r.status_code == 400


def test_update_deal(auth_client):
    cr = auth_client.post("/api/deals",
        data=json.dumps({"title": "Update Deal"}),
        content_type="application/json")
    did = cr.json["id"]
    r = auth_client.put(f"/api/deals/{did}",
        data=json.dumps({"title": "Updated Deal", "value": 99999}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["title"] == "Updated Deal"


def test_move_deal_stage(auth_client):
    cr = auth_client.post("/api/deals",
        data=json.dumps({"title": "Move Deal", "stage": "New Lead"}),
        content_type="application/json")
    did = cr.json["id"]
    r = auth_client.patch(f"/api/deals/{did}/stage",
        data=json.dumps({"stage": "Contacted"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["stage"] == "Contacted"


def test_move_deal_invalid_stage(auth_client):
    cr = auth_client.post("/api/deals",
        data=json.dumps({"title": "Bad Stage Deal"}),
        content_type="application/json")
    did = cr.json["id"]
    r = auth_client.patch(f"/api/deals/{did}/stage",
        data=json.dumps({"stage": "Invalid Stage"}),
        content_type="application/json")
    assert r.status_code == 400


def test_delete_deal(auth_client):
    cr = auth_client.post("/api/deals",
        data=json.dumps({"title": "Delete Deal"}),
        content_type="application/json")
    did = cr.json["id"]
    r = auth_client.delete(f"/api/deals/{did}")
    assert r.status_code == 200


# --- Dashboard ---

def test_dashboard_stats(auth_client):
    r = auth_client.get("/api/dashboard-stats")
    assert r.status_code == 200
    data = r.json
    assert "total_contacts" in data
    assert "total_leads" in data
    assert "pipeline_value" in data
    assert "total_revenue" in data
    assert "deals_by_stage" in data
    assert "recent_activity" in data


# --- Pages ---

def test_landing_page(client):
    r = client.get("/lp")
    assert r.status_code == 200


def test_sales_page(client):
    r = client.get("/sales")
    assert r.status_code == 200


def test_form_submission_creates_contact(auth_client):
    # Submit landing form
    auth_client.post("/lp/submit", data={"name": "Form Lead", "email": "form@test.com"}, follow_redirects=True)
    # Verify contact was created
    r = auth_client.get("/api/contacts?q=Form+Lead")
    assert r.status_code == 200
    assert any(c["name"] == "Form Lead" for c in r.json)
