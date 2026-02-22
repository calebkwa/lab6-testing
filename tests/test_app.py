import pytest

from app import app, db
from models import Contact


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Configure app for testing
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    # Create test client
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_contact(client):
    """Create a sample contact in the database"""
    contact = Contact(
        name="John Doe",
        phone="1234567890",
        email="john@example.com",
        type="Personal",
    )
    db.session.add(contact)
    db.session.commit()
    return contact


def test_index_page(client):
    """Test that the home page loads successfully"""
    response = client.get("/")
    assert response.status_code == 200


def test_add_contact(client):
    """Test adding a new contact through the web form"""
    data = {
        "name": "Jane Doe",
        "phone": "9876543210",
        "email": "jane@example.com",
        "type": "Personal",
        "submit": "Submit",
    }
    response = client.post("/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Jane Doe" in response.data


def test_update_contact(client, sample_contact):
    """Test updating an existing contact"""
    data = {
        "name": "John Smith",
        "phone": sample_contact.phone,
        "email": sample_contact.email,
        "type": sample_contact.type,
        "submit": "Update",
    }
    response = client.post(
        f"/update/{sample_contact.id}",
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    updated_contact = db.session.get(Contact, sample_contact.id)
    assert updated_contact.name == "John Smith"


def test_get_contacts_api(client, sample_contact):
    """Test retrieving all contacts via API"""
    response = client.get("/api/contacts")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "John Doe"


def test_create_contact_api(client):
    """Test creating a contact via API"""
    data = {
        "name": "API User",
        "phone": "5555555555",
        "email": "api@example.com",
        "type": "Work",
    }
    response = client.post("/api/contacts", json=data)
    assert response.status_code == 201
    assert response.get_json()["name"] == "API User"


def test_get_nonexistent_contact(client):
    """Test error handling for nonexistent contact"""
    response = client.get("/api/contacts/999")
    assert response.status_code == 404
