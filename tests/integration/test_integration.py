"""Integration tests for FastAPI Product Catalog REST endpoints."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.database import get_session
from src.main import app

# Configurable test database URL via environment variable with SQLite fallback
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_integration.db")
connect_args = {"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
test_engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)


def get_test_session():
    """Yield a database session connected to the test database."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Setup and teardown database schema before and after running test module."""
    SQLModel.metadata.create_all(test_engine)
    app.dependency_overrides[get_session] = get_test_session
    yield
    SQLModel.metadata.drop_all(test_engine)
    app.dependency_overrides.clear()
    # Clean up SQLite test file if present
    if "test_integration.db" in TEST_DATABASE_URL and os.path.exists("./test_integration.db"):
        try:
            os.remove("./test_integration.db")
        except OSError:
            pass


@pytest.fixture(name="client")
def client_fixture():
    """Provide a TestClient instance for issuing requests."""
    with TestClient(app) as client:
        yield client


def test_root_endpoint(client: TestClient):
    """Assert GET / returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Product Catalog API"
    assert data["status"] == "online"


def test_health_endpoint(client: TestClient):
    """Assert GET /health returns status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_product_success(client: TestClient):
    """Assert POST /products returns 201 Created and product data."""
    payload = {
        "name": "4K Ultra HD Monitor",
        "description": "27-inch IPS 4K HDR monitor with USB-C 90W charging",
        "price": 399.99,
        "stock": 40,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]


def test_create_product_validation_failure_negative_price(client: TestClient):
    """Assert POST /products rejects non-positive price with 422."""
    payload = {
        "name": "Invalid Product",
        "description": "Product with negative price",
        "price": -10.0,
        "stock": 10,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422


def test_create_product_validation_failure_negative_stock(client: TestClient):
    """Assert POST /products rejects negative stock with 422."""
    payload = {
        "name": "Invalid Product",
        "description": "Product with negative stock",
        "price": 10.0,
        "stock": -5,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422


def test_create_product_validation_missing_fields(client: TestClient):
    """Assert POST /products rejects missing required fields with 422."""
    payload = {
        "description": "Missing name and price",
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422


def test_get_all_products(client: TestClient):
    """Assert GET /products returns list of stored products."""
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_product_by_id_success(client: TestClient):
    """Assert GET /products/{id} returns the specific product."""
    create_res = client.post(
        "/products",
        json={
            "name": "Noise Cancelling Headphones",
            "description": "Over-ear wireless Bluetooth headphones with ANC",
            "price": 199.99,
            "stock": 75,
        },
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Noise Cancelling Headphones"


def test_get_product_by_id_not_found(client: TestClient):
    """Assert GET /products/{id} returns 404 for non-existent ID."""
    response = client.get("/products/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product with ID 999999 not found"


def test_update_product_success(client: TestClient):
    """Assert PUT /products/{id} updates and returns updated product."""
    create_res = client.post(
        "/products",
        json={
            "name": "Smart Speaker",
            "description": "Voice-controlled smart assistant speaker",
            "price": 49.99,
            "stock": 30,
        },
    )
    product_id = create_res.json()["id"]

    update_payload = {"price": 44.99, "stock": 25}
    response = client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["price"] == 44.99
    assert data["stock"] == 25
    assert data["name"] == "Smart Speaker"


def test_update_product_not_found(client: TestClient):
    """Assert PUT /products/{id} returns 404 when product is missing."""
    response = client.put("/products/999999", json={"price": 10.0})
    assert response.status_code == 404


def test_delete_product_success(client: TestClient):
    """Assert DELETE /products/{id} deletes the item with 204 status."""
    create_res = client.post(
        "/products",
        json={
            "name": "Temporary Item",
            "description": "Item to be deleted",
            "price": 9.99,
            "stock": 5,
        },
    )
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code == 204

    # Verify item is gone
    get_res = client.get(f"/products/{product_id}")
    assert get_res.status_code == 404


def test_delete_product_not_found(client: TestClient):
    """Assert DELETE /products/{id} returns 404 when product is missing."""
    response = client.delete("/products/999999")
    assert response.status_code == 404
