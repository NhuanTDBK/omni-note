import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from PIL import Image
import io

from app.api.deps import get_db, get_current_user
from app.main import app
from app.adapters.persistance.base import Base

# Create in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return "test_user"


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_material():
    return {
        "title": "Test Material",
        "content": "Test Content",
        "tags": ["test", "material"],
    }


def test_create_material(test_material):
    response = client.post("/api/v1/materials/", json=test_material)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_material["title"]
    assert data["content"] == test_material["content"]
    assert data["tags"] == test_material["tags"]
    return data


def test_get_material(test_material):
    # First create a material
    created = test_create_material(test_material)

    # Then get it
    response = client.get(f"/api/v1/materials/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_material["title"]


def test_list_materials(test_material):
    # Create a material first
    test_create_material(test_material)

    response = client.get("/api/v1/materials/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_update_material(test_material):
    # First create a material
    created = test_create_material(test_material)

    # Update it
    updated_data = {
        "title": "Updated Title",
        "content": "Updated Content",
        "tags": ["updated"],
    }
    response = client.put(f"/api/v1/materials/{created['id']}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]
    assert data["tags"] == updated_data["tags"]


def test_delete_material(test_material):
    # First create a material
    created = test_create_material(test_material)

    # Delete it
    response = client.delete(f"/api/v1/materials/{created['id']}")
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/api/v1/materials/{created['id']}")
    assert response.status_code == 404


def test_extract_data():
    # Create a test image
    img = Image.new("RGB", (60, 30), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    files = [("files", ("test.png", img_byte_arr, "image/png"))]
    texts = ["Test text for extraction"]

    response = client.post("/api/v1/extract_data", files=files, data={"texts": texts})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
