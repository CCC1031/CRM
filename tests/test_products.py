"""Tests for Products & eCommerce features."""
import json


# --- Products API ---

def test_create_product(auth_client):
    r = auth_client.post("/api/products",
        data=json.dumps({"name": "Test Product", "price": 49.99, "product_type": "paid"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["name"] == "Test Product"
    assert r.json["price"] == 49.99
    assert r.json["product_type"] == "paid"
    assert r.json["active"] is True


def test_create_product_requires_name(auth_client):
    r = auth_client.post("/api/products",
        data=json.dumps({"price": 10}),
        content_type="application/json")
    assert r.status_code == 400


def test_create_free_product(auth_client):
    r = auth_client.post("/api/products",
        data=json.dumps({"name": "Free Guide", "price": 0, "product_type": "free"}),
        content_type="application/json")
    assert r.status_code == 201
    assert r.json["product_type"] == "free"
    assert r.json["price"] == 0


def test_update_product(auth_client):
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Update Me"}),
        content_type="application/json")
    pid = cr.json["id"]
    r = auth_client.put(f"/api/products/{pid}",
        data=json.dumps({"name": "Updated Product", "price": 99.99, "active": False}),
        content_type="application/json")
    assert r.status_code == 200
    assert r.json["name"] == "Updated Product"
    assert r.json["price"] == 99.99
    assert r.json["active"] is False


def test_delete_product(auth_client):
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Delete Me"}),
        content_type="application/json")
    pid = cr.json["id"]
    r = auth_client.delete(f"/api/products/{pid}")
    assert r.status_code == 200
    assert "deleted" in r.json["message"].lower()


def test_delete_nonexistent_product(auth_client):
    r = auth_client.delete("/api/products/9999")
    assert r.status_code == 404


# --- Mock Checkout ---

def test_mock_checkout(auth_client):
    # Create a product first
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Checkout Product", "price": 47, "product_type": "paid"}),
        content_type="application/json")
    pid = cr.json["id"]
    r = auth_client.post(f"/api/checkout/{pid}",
        data=json.dumps({"name": "Buyer", "email": "buyer@test.com"}),
        content_type="application/json")
    assert r.status_code == 200
    data = r.json
    assert data["mock"] is True
    assert "checkout_url" in data
    assert "session_id" in data


def test_mock_checkout_creates_purchase(auth_client):
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Purchase Track", "price": 97, "product_type": "paid"}),
        content_type="application/json")
    pid = cr.json["id"]
    auth_client.post(f"/api/checkout/{pid}",
        data=json.dumps({"name": "Track Buyer", "email": "track@test.com"}),
        content_type="application/json")
    # Check contact was created
    r = auth_client.get("/api/contacts?q=Track+Buyer")
    assert r.status_code == 200
    assert any(c["email"] == "track@test.com" for c in r.json)


def test_checkout_inactive_product(auth_client):
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Inactive", "active": True}),
        content_type="application/json")
    pid = cr.json["id"]
    # Deactivate
    auth_client.put(f"/api/products/{pid}",
        data=json.dumps({"active": False}),
        content_type="application/json")
    r = auth_client.post(f"/api/checkout/{pid}",
        data=json.dumps({}),
        content_type="application/json")
    assert r.status_code == 400


# --- Pages ---

def test_products_page(auth_client):
    r = auth_client.get("/admin/products")
    assert r.status_code == 200


def test_product_detail_page(auth_client):
    cr = auth_client.post("/api/products",
        data=json.dumps({"name": "Detail Product"}),
        content_type="application/json")
    pid = cr.json["id"]
    r = auth_client.get(f"/admin/products/{pid}")
    assert r.status_code == 200


def test_products_filter_active(auth_client):
    r = auth_client.get("/admin/products?status=active")
    assert r.status_code == 200


def test_store_page(client):
    r = client.get("/store")
    assert r.status_code == 200


def test_checkout_success_page(client):
    r = client.get("/checkout/success?session_id=mock_test123")
    assert r.status_code == 200


def test_checkout_cancel_page(client):
    r = client.get("/checkout/cancel")
    assert r.status_code == 200
