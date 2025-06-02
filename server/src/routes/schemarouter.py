from datetime import datetime
from typing import List, Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, Body, Depends

from src.basemodels.schema_base_models import SchemaDeletedResponse, PyObjectId
from src.basemodels.schema_base_models import CreatedSchemaResponse, CreateSchemaRequest, InsertedSchema, SchemaUpdateRequest
from src.db import get_db

router = APIRouter()

async def __get_schema(_id: str, collection) -> InsertedSchema:
    """
    Retrieve a schema from the database by its ID.

    Parameters:
    - _id (str): The ID of the schema to retrieve.
    - collection: The database collection to search in.

    Returns:
    - InsertedSchema: The retrieved schema.

    Raises:
    - HTTPException: If the schema is not found, a 404 error is raised.
    """
    schema = await collection.find_one({"_id": ObjectId(_id)})
    if schema is None:
        raise HTTPException(status_code=404, detail="Schema not found")

    res_model = InsertedSchema(**schema)
    return res_model

@router.post("/", response_model=CreatedSchemaResponse, response_model_exclude_none=True)
async def create_schema(schema: CreateSchemaRequest, db=Depends(get_db)):
    """
    Create a new schema in the database.

    Parameters:
    - schema (CreateSchemaRequest): The schema data to create.
    - db: The database dependency.

    Returns:
    - CreatedSchemaResponse: The response containing the created schema.

    Raises:
    - HTTPException: If a schema with the same name already exists, a 400 error is raised.
    """
    collection = db['schemas']
    existing_schema = await collection.find_one({"schema_name": schema.schema_name})
    if existing_schema:
        raise HTTPException(status_code=400, detail="Schema already exists")

    schema_data = schema.model_dump(exclude_unset=True, exclude_none=True)

    now = datetime.now()
    schema_data['created_at'] = now  # Add created_at field
    schema_data["updated_at"] = now
    result = await collection.insert_one(schema_data)

    res = {
        "_id": result.inserted_id,
        "message": "Schema created successfully",
        "data": schema_data
    }

    res_model = CreatedSchemaResponse(**res)
    return res_model

@router.get("/", response_model=List[InsertedSchema], response_model_exclude_none=True)
async def read_schemas(db=Depends(get_db)):
    """
    Retrieve all schemas from the database.

    Parameters:
    - db: The database dependency.

    Returns:
    - List[InsertedSchema]: A list of all schemas.

    """
    collection = db['schemas']

    schemas = []
    async for schema in collection.find():
        schemas.append(InsertedSchema(**schema))  # Correctly format schema
    return schemas

@router.get("/{schema_id}", response_model=InsertedSchema, response_model_exclude_none=True)
async def read_schema(schema_id: str, db=Depends(get_db)):
    """
    Retrieve a specific schema by its ID.

    Parameters:
    - schema_id (str): The ID of the schema to retrieve.
    - db: The database dependency.

    Returns:
    - InsertedSchema: The retrieved schema.

    Raises:
    - HTTPException: If the schema is not found, a 404 error is raised.
    """
    return await __get_schema(schema_id, db["schemas"])

@router.put("/{schema_id}", response_model=InsertedSchema, response_model_exclude_none=True)
async def update_schema(
    schema_id: Annotated[str, Path(title="The schema id to update")],
    schema: Annotated[SchemaUpdateRequest, Body(title="The parameters to be updated")],
    db=Depends(get_db)
):
    """
    Update an existing schema in the database.

    Parameters:
    - schema_id (str): The ID of the schema to update.
    - schema (SchemaUpdateRequest): The updated schema data.
    - db: The database dependency.

    Returns:
    - InsertedSchema: The updated schema.

    Raises:
    - HTTPException: If the schema is not found, a 404 error is raised.
    """
    collection = db["schemas"]
    update_dict = schema.model_dump(exclude_none=True)
    update_dict["updated_at"] = datetime.now()
    result = await collection.update_one({"_id": ObjectId(schema_id)}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")

    latest = await __get_schema(schema_id, collection)
    return latest

@router.delete("/{schema_id}", response_model=SchemaDeletedResponse, response_model_exclude_none=True)
async def delete_schema(schema_id: str, db=Depends(get_db)):
    """
    Delete a schema from the database by its ID.

    Parameters:
    - schema_id (str): The ID of the schema to delete.
    - db: The database dependency.

    Returns:
    - SchemaDeletedResponse: The response indicating the schema was deleted.

    Raises:
    - HTTPException: If the schema is not found, a 404 error is raised.
    """
    _id = PyObjectId(schema_id)
    collection = db["schemas"]

    result = await collection.delete_one({"_id": _id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")
    return SchemaDeletedResponse(_id=_id, detail="Schema deleted successfully")
