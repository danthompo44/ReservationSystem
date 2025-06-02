import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient
from fastapi import FastAPI

from src.basemodels.schema_base_models import CreateSchemaRequest, FieldDefinition
from src.routes.schemarouter import router
from src.db import db  # Importing db here

app = FastAPI()
app.include_router(prefix="/schemas", router=router)

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
    fields = {
        "msisdn": FieldDefinition(type="str", required=True, regex="44\d{9}"),
        "imsi": FieldDefinition(type="str", required=True, regex="23(0|3)\d{12}"),
        "environment": FieldDefinition(type="str", required=True, enum=["Dev_1", "Dev_2", "Stable_1", "Stable2"])
    }
    req = CreateSchemaRequest(schema_name="SIM", fields=fields)
    response = test_client.post("/schemas/", json=req.model_dump(exclude_none=True))
    assert response.status_code == 200
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
