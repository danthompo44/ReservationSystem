import mongomock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.basemodels.schema_base_models import CreateSchemaRequest, PyObjectId
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
        "msisdn": {
            "type": "str",
            "required": True,
            "regex": r"44\d{9}"
        },
        "imsi": {
            "type": "str",
            "required": True,
            "regex": r"23(0|3)\d{12}"
        },
        "environment": {
            "type": "str",
            "required": True,
            "enum": ["Dev_1", "Dev_2", "Stable_1", "Stable2"]
        }
    }
    return {
        "schema_name": "SIM",
        "fields": fields
    }


def __ue_schema() -> CreateSchemaRequest:
    """Helper function to create a sample UE schema request."""
    fields = {
        "os": {
            "type": "str",
            "required": True,
            "enum": ["android", "iOS"]
        },
        "device_id": {
            "type": "str",
            "required": True
        }
    }
    return {
        "schema_name": "UE",
        "fields": fields
    }


def __building_schema() -> CreateSchemaRequest:
    """Helper function to create a sample Building schema request."""
    fields = {
        "country": {
            "type": "str",
            "required": True,
            "enum": ["GB", "US", "DE", "FR"]
        },
        "city": {
            "type": "str",
            "required": True
        }
    }
    return {
        "schema_name": "Building",
        "fields": fields
    }


def __house_schema() -> CreateSchemaRequest:
    """Helper function to create a sample House schema request."""
    fields = {
        "country": {
            "type": "str",
            "required": True,
            "enum": ["GB", "US", "DE", "FR"]
        },
        "city": {
            "type": "str",
            "required": True
        },
        "address": {
            "type": "str",
            "required": True
        },
        "floor": {
            "type": "int",
            "required": True,
            "min": 1,
            "max": 100
        }
    }
    return {
        "schema_name": "House",
        "fields": fields
    }


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


def test_create_schema_with_invalid_string_constraints(test_client):
    """Test that a 422 response is returned when a string FieldDefinition has min/max constraints."""
    invalid_schema = {
        "schema_name": "InvalidStringSchema",
        "fields": {
            "field1": {
                "type": "str",
                "min": 1,
                "max": 10
            }
        }
    }
    response = test_client.post("/schemas/", json=invalid_schema)
    assert response.status_code == 422


def test_create_schema_with_invalid_int_constraints(test_client):
    """Test that a 422 response is returned when an integer FieldDefinition has min_length/max_length constraints."""
    invalid_schema = {
        "schema_name": "InvalidIntSchema",
        "fields": {
            "field1": {
                "type": "int",
                "min_length": 1
            }
        }
    }
    response = test_client.post("/schemas/", json=invalid_schema)
    assert response.status_code == 422


def test_create_schema_with_invalid_float_constraints(test_client):
    """Test that a 422 response is returned when a float FieldDefinition has min_length/max_length constraints."""
    invalid_schema = {
        "schema_name": "InvalidFloatSchema",
        "fields": {
            "field1": {
                "type": "float",
                "min_length": 1
            }
        }
    }
    response = test_client.post("/schemas/", json=invalid_schema)
    assert response.status_code == 422


def test_create_schema_with_invalid_boolean_constraints(test_client):
    """Test that a 422 response is returned when a boolean FieldDefinition has min/max constraints."""
    invalid_schema = {
        "schema_name": "InvalidBooleanSchema",
        "fields": {
            "field1": {
                "type": "boolean",
                "min": 0,
                "max": 1
            }
        }
    }
    response = test_client.post("/schemas/", json=invalid_schema)
    assert response.status_code == 422


def test_create_schema_with_invalid_list_constraints(test_client):
    """Test that a 422 response is returned when a list FieldDefinition has min/max constraints."""
    invalid_schema = {
        "schema_name": "InvalidListSchema",
        "fields": {
            "field1": {
                "type": "list",
                "min": 1,
                "max": 10
            }
        }
    }
    response = test_client.post("/schemas/", json=invalid_schema)
    assert response.status_code == 422
