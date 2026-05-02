"""Tests for Clients features."""
import json


# --- Client Pages ---

def test_clients_page(auth_client):
    r = auth_client.get("/admin/clients")
    assert r.status_code == 200


def test_clients_page_archived(auth_client):
    r = auth_client.get("/admin/clients?archived=true")
    assert r.status_code == 200


def test_client_detail_page(auth_client):
    # Create a client contact
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Client Detail Test", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.get(f"/admin/clients/{cid}")
    assert r.status_code == 200


# --- Client Notes ---

def test_add_client_note(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Note Client", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.post(f"/api/clients/{cid}/notes",
        data=json.dumps({"title": "Meeting Notes", "content": "**Bold** text and *italic*"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["title"] == "Meeting Notes"
    assert "Bold" in r.json["content"]


def test_add_client_note_requires_fields(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Missing Fields", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.post(f"/api/clients/{cid}/notes",
        data=json.dumps({"title": "No content"}),
        content_type="application/json")
    assert r.status_code == 400


def test_edit_client_note(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Edit Note Client", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    nr = auth_client.post(f"/api/clients/{cid}/notes",
        data=json.dumps({"title": "Original", "content": "Original content"}),
        content_type="application/json")
    nid = nr.json["id"]
    r = auth_client.put(f"/api/clients/{cid}/notes/{nid}",
        data=json.dumps({"title": "Updated", "content": "Updated content"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["title"] == "Updated"
    assert r.json["content"] == "Updated content"


def test_delete_client_note(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Delete Note Client", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    nr = auth_client.post(f"/api/clients/{cid}/notes",
        data=json.dumps({"title": "Delete Me", "content": "Will be deleted"}),
        content_type="application/json")
    nid = nr.json["id"]
    r = auth_client.delete(f"/api/clients/{cid}/notes/{nid}")
    assert r.status_code == 200


# --- Archive ---

def test_archive_client(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Archive Test", "status": "Client"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.patch(f"/api/clients/{cid}/archive",
        data=json.dumps({}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["status"] == "Archived"


def test_unarchive_client(auth_client):
    cr = auth_client.post("/api/contacts",
        data=json.dumps({"name": "Unarchive Test", "status": "Archived"}),
        content_type="application/json")
    cid = cr.json["id"]
    r = auth_client.patch(f"/api/clients/{cid}/archive",
        data=json.dumps({}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["status"] == "Client"
