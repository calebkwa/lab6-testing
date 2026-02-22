import pytest

from app import app
from models import db, Contact


@pytest.fixture()
def client():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_get_contacts_empty(client):
    response = client.get("/api/contacts")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_contact_success(client):
    payload = {
        "name": "Ada Lovelace",
        "phone": "555-0101",
        "email": "ada@example.com",
        "type": "Work",
    }
    response = client.post("/api/contacts", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["email"] == payload["email"]
    assert data["type"] == payload["type"]


def test_create_contact_missing_fields(client):
    response = client.post("/api/contacts", json={"name": "Missing Phone"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing required fields"


def test_update_contact_success(client):
    with app.app_context():
        contact = Contact(name="Grace Hopper", phone="555-0202", email="", type="Work")
        db.session.add(contact)
        db.session.commit()
        contact_id = contact.id

    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"phone": "555-0203", "type": "Personal"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["phone"] == "555-0203"
    assert data["type"] == "Personal"


def test_delete_contact_success(client):
    with app.app_context():
        contact = Contact(name="Alan Turing", phone="555-0303", email=None, type="Other")
        db.session.add(contact)
        db.session.commit()
        contact_id = contact.id

    delete_response = client.delete(f"/api/contacts/{contact_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/contacts/{contact_id}")
    assert get_response.status_code == 404
