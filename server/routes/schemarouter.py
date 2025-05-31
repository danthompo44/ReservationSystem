from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from server.routes.basemodels import InsertedSchemaResponse, SchemaInsertRequest
from utils import datetime_as_string

router = APIRouter()

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client['reservation-system']
collection = db['schemas']


@router.post("/", response_model=InsertedSchemaResponse)
async def create_schema(schema: SchemaInsertRequest):
    existing_schema = await collection.find_one({"name": schema.name})
    if existing_schema:
        raise HTTPException(status_code=400, detail="Schema already exists")

    schema_data = schema.model_dump()
    schema_data['created_at'] = datetime_as_string(datetime.now())# Add created_at field
    result = await collection.insert_one(schema_data)
    schema_data.pop('_id')

    res = {
        "id": str(result.inserted_id),
        "message": "Schema created successfully",
        "data": schema_data
    }
    return res


@router.get("/")
async def read_schemas():
    schemas = []
    async for schema in collection.find():
        schemas.append({**schema, "_id": str(schema["_id"])})  # Correctly format schema
    return schemas


@router.get("/{schema_id}")
async def read_schema(schema_id: str):
    schema = await collection.find_one({"_id": ObjectId(schema_id)})
    if schema is None:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {**schema, "_id": str(schema["_id"])}


@router.put("/{schema_id}")
async def update_schema(schema_id: str, schema):
    result = await collection.update_one({"_id": ObjectId(schema_id)}, {"$set": schema.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {**schema.dict(), "_id": schema_id}


@router.delete("/{schema_id}")
async def delete_schema(schema_id: str):
    result = await collection.delete_one({"_id": ObjectId(schema_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {"detail": "Schema deleted"}
