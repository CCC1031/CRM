"""Tests for Tasks features."""
import json


# --- Tasks API ---

def test_create_task(auth_client):
    r = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Test Task", "priority": "high", "status": "todo"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["title"] == "Test Task"
    assert r.json["priority"] == "high"
    assert r.json["status"] == "todo"


def test_create_task_requires_title(auth_client):
    r = auth_client.post("/api/tasks",
        data=json.dumps({"priority": "low"}),
        content_type="application/json")
    assert r.status_code == 400


def test_create_task_with_description_and_due_date(auth_client):
    r = auth_client.post("/api/tasks",
        data=json.dumps({
            "title": "Detailed Task",
            "description": "Do something important",
            "priority": "medium",
            "due_date": "2026-06-15"
        }),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["description"] == "Do something important"
    assert r.json["due_date"] == "2026-06-15"


def test_update_task(auth_client):
    cr = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Update Task"}),
        content_type="application/json")
    tid = cr.json["id"]
    r = auth_client.put(f"/api/tasks/{tid}",
        data=json.dumps({"title": "Updated Task", "priority": "low"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["title"] == "Updated Task"
    assert r.json["priority"] == "low"


def test_move_task_status(auth_client):
    cr = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Move Task", "status": "todo"}),
        content_type="application/json")
    tid = cr.json["id"]
    r = auth_client.patch(f"/api/tasks/{tid}/status",
        data=json.dumps({"status": "in_progress"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["status"] == "in_progress"


def test_move_task_invalid_status(auth_client):
    cr = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Bad Status Task"}),
        content_type="application/json")
    tid = cr.json["id"]
    r = auth_client.patch(f"/api/tasks/{tid}/status",
        data=json.dumps({"status": "invalid"}),
        content_type="application/json")
    assert r.status_code == 400


def test_delete_task(auth_client):
    cr = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Delete Task"}),
        content_type="application/json")
    tid = cr.json["id"]
    r = auth_client.delete(f"/api/tasks/{tid}")
    assert r.status_code == 200


def test_complete_task(auth_client):
    cr = auth_client.post("/api/tasks",
        data=json.dumps({"title": "Complete Task", "status": "in_progress"}),
        content_type="application/json")
    tid = cr.json["id"]
    r = auth_client.patch(f"/api/tasks/{tid}/status",
        data=json.dumps({"status": "done"}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["status"] == "done"


# --- Pages ---

def test_tasks_page(auth_client):
    r = auth_client.get("/admin/tasks")
    assert r.status_code == 200
