from datetime import datetime
from typing import List, Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, Body
from motor.motor_asyncio import AsyncIOMotorClient

from routes.basemodels import SchemaDeletedResponse, PyObjectId
from server.routes.basemodels import CreatedSchemaResponse, SchemaInsertRequest, InsertedSchema, SchemaUpdateRequest

router = APIRouter()

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client['reservation-system']
collection = db['schemas']

async def __get_schema(_id) -> InsertedSchema:
    schema = await collection.find_one({"_id": ObjectId(_id)})
    if schema is None:
        raise HTTPException(status_code=404, detail="Schema not found")  #

    res_model = InsertedSchema(**schema)
    return res_model



@router.post("/", response_model=CreatedSchemaResponse)
async def create_schema(schema: SchemaInsertRequest):
    existing_schema = await collection.find_one({"name": schema.name})
    if existing_schema:
        raise HTTPException(status_code=400, detail="Schema already exists")

    schema_data = schema.model_dump()
    now = datetime.now()
    schema_data['created_at'] = now # Add created_at field
    schema_data["updated_at"] = now
    result = await collection.insert_one(schema_data)

    res = {
        "_id": result.inserted_id,
        "message": "Schema created successfully",
        "data": schema_data
    }

    res_model = CreatedSchemaResponse(**res)
    return res_model


@router.get("/", response_model=List[InsertedSchema])
async def read_schemas():
    schemas = []
    async for schema in collection.find():
        schemas.append(InsertedSchema(**schema))  # Correctly format schema
    return schemas


@router.get("/{schema_id}", response_model=InsertedSchema)
async def read_schema(schema_id: str):
    return await __get_schema(schema_id)


@router.put("/{schema_id}", response_model=InsertedSchema)
async def update_schema(
    schema_id: Annotated[str, Path(title="The schema id to update")],
    schema: Annotated[SchemaUpdateRequest, Body(title="The parameters to be updated")]
):
    update_dict = schema.model_dump()
    update_dict["updated_at"] = datetime.now()
    result = await collection.update_one({"_id": ObjectId(schema_id)}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")

    latest = await __get_schema(schema_id)
    return latest


@router.delete("/{schema_id}", response_model=SchemaDeletedResponse)
async def delete_schema(schema_id: str):
    _id = PyObjectId(schema_id)

    result = await collection.delete_one({"_id": _id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")
    return SchemaDeletedResponse(_id=_id, detail="Schema deleted successfully")
