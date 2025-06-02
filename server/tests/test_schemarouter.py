import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient
from fastapi import FastAPI
from src.routes.schemarouter import router
from src.db import db  # Importing db here

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@pytest.fixture
def mongo_client():
    client = MongoClient()
    yield client
    client.drop_database('reservation-system')

@pytest.fixture
def test_client(mongo_client):
    app.dependency_overrides[db] = lambda: mongo_client['reservation-system']
    yield TestClient(app)

def test_create_schema(test_client):
    response = test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    assert response.status_code == 201
    assert response.json()["message"] == "Schema created successfully"

def test_create_schema_already_exists(test_client):
    test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    response = test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Schema already exists"

def test_read_schemas(test_client):
    test_client.post("/schemas/", json={"schema_name": "Test Schema 1"})
    test_client.post("/schemas/", json={"schema_name": "Test Schema 2"})
    response = test_client.get("/schemas/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_read_schema(test_client):
    response = test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    schema_id = response.json()["_id"]
    response = test_client.get(f"/schemas/{schema_id}")
    assert response.status_code == 200
    assert response.json()["data"]["schema_name"] == "Test Schema"

def test_read_schema_not_found(test_client):
    response = test_client.get("/schemas/invalid_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"

def test_update_schema(test_client):
    response = test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    schema_id = response.json()["_id"]
    response = test_client.put(f"/schemas/{schema_id}", json={"schema_name": "Updated Schema"})
    assert response.status_code == 200
    assert response.json()["data"]["schema_name"] == "Updated Schema"

def test_update_schema_not_found(test_client):
    response = test_client.put("/schemas/invalid_id", json={"schema_name": "Updated Schema"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"

def test_delete_schema(test_client):
    response = test_client.post("/schemas/", json={"schema_name": "Test Schema"})
    schema_id = response.json()["_id"]
    response = test_client.delete(f"/schemas/{schema_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Schema deleted successfully"

def test_delete_schema_not_found(test_client):
    response = test_client.delete("/schemas/invalid_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"
