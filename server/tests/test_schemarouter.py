import mongomock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.basemodels.schema_base_models import CreateSchemaRequest, FieldDefinition, PyObjectId
from src.db import get_db  # Importing db here
from src.routes.schemarouter import router
from tests.AsyncMongoMock import AsyncMockDB

# Create FastAPI app and include router
app = FastAPI()
app.include_router(prefix="/schemas", router=router)

# === Shared mongomock client across tests ===
@pytest.fixture(scope="session")
def mock_sync_client():
    """Fixture to create a synchronous MongoDB client for testing."""
    return mongomock.MongoClient()


@pytest.fixture(scope="session")
def async_mock_db(mock_sync_client):
    """Fixture to create an asynchronous mock database for testing."""
    return AsyncMockDB(mock_sync_client["reservation-system"])


@pytest.fixture(scope="session")
def test_client(async_mock_db):
    """Fixture to create a test client for the FastAPI app with overridden database dependency."""
    async def override_get_db():
        yield async_mock_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def __sim_schema() -> CreateSchemaRequest:
    """Helper function to create a sample SIM schema request."""
    fields = {
        "msisdn": FieldDefinition(type="str", required=True, regex=r"44\d{9}"),
        "imsi": FieldDefinition(type="str", required=True, regex=r"23(0|3)\d{12}"),
        "environment": FieldDefinition(type="str", required=True, enum=["Dev_1", "Dev_2", "Stable_1", "Stable2"])
    }
    req = CreateSchemaRequest(schema_name="SIM", fields=fields)

    return req.model_dump(exclude_none=True)


def __ue_schema() -> CreateSchemaRequest:
    """Helper function to create a sample UE schema request."""
    fields = {
        "os": FieldDefinition(type="str", required=True, enum=["android", "iOS"]),
        "device_id": FieldDefinition(type="str", required=True)
    }

    req = CreateSchemaRequest(schema_name="UE", fields=fields)

    return req.model_dump(exclude_none=True)


def __building_schema() -> CreateSchemaRequest:
    """Helper function to create a sample Building schema request."""
    fields = {
        "country": FieldDefinition(type="str", required=True, enum=["GB", "US", "DE", "FR"]),
        "city": FieldDefinition(type="str", required=True)
    }
    req = CreateSchemaRequest(schema_name="Building", fields=fields)

    return req.model_dump(exclude_none=True)


def __house_schema() -> CreateSchemaRequest:
    """Helper function to create a sample House schema request."""
    fields = {
        "country": FieldDefinition(type="str", required=True, enum=["GB", "US", "DE", "FR"]),
        "city": FieldDefinition(type="str", required=True),
        "address": FieldDefinition(type="str", required=True),
        "floor": FieldDefinition(type="int", required=True, min=1, max=100)
    }
    req = CreateSchemaRequest(schema_name="House", fields=fields)
    return req.model_dump(exclude_none=True)


def test_create_schema(test_client):
    """Test the creation of a new schema."""
    response = test_client.post("/schemas/", json=__sim_schema())
    assert response.status_code == 200
    assert response.json()["message"] == "Schema created successfully"


def test_create_schema_already_exists(test_client):
    """Test the behaviour when trying to create a schema that already exists."""
    response = test_client.post("/schemas/", json=__sim_schema())
    assert response.status_code == 400
    assert response.json()["detail"] == "Schema already exists"


def test_read_schemas(test_client):
    """Test retrieving all schemas."""
    test_client.post("/schemas/", json=__sim_schema())
    test_client.post("/schemas/", json=__ue_schema())
    response = test_client.get("/schemas/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_schema(test_client):
    """Test retrieving a specific schema by ID."""
    response = test_client.get("/schemas/")
    body = response.json()
    # Get the first schema in the list, retrieve its ID ready for testing get_schema
    schema_id = response.json()[0]["_id"]
    response = test_client.get(f"/schemas/{schema_id}")
    assert response.status_code == 200
    # Call SIM schema as that will be the first object in the db
    assert response.json()["schema_name"] == __sim_schema()["schema_name"]


def test_read_schema_not_found(test_client):
    """Test the behaviour when trying to read a schema that does not exist."""
    response = test_client.get(f"/schemas/{PyObjectId()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"


def test_update_schema(test_client):
    """Test updating an existing schema."""
    response = test_client.post("/schemas/", json=__building_schema())
    schema_id = response.json()["_id"]

    enum = ["GB", "US", "DE", "FR", "BE", "ROM"]
    response = test_client.put(f"/schemas/{schema_id}", json={"fields": {
        "country": {
            "enum": enum
        },
    }})
    assert response.status_code == 200
    assert response.json()["fields"]["country"]["enum"] == enum


def test_update_schema_not_found(test_client):
    """Test the behaviour when trying to update a schema that does not exist."""
    enum = ["GB", "US", "DE", "FR", "BE", "ROM"]
    response = test_client.put(f"/schemas/{PyObjectId()}", json={"fields": {
        "country": {
            "enum": enum
        },
    }})
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"


def test_delete_schema(test_client):
    """Test deleting an existing schema."""
    response = test_client.post("/schemas/", json=__house_schema())
    schema_id = response.json()["_id"]
    response = test_client.delete(f"/schemas/{schema_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Schema deleted successfully"


def test_delete_schema_not_found(test_client):
    """Test the behaviour when trying to delete a schema that does not exist."""
    response = test_client.delete(f"/schemas/{PyObjectId()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"
