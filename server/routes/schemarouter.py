from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from server.routes.basemodels import CreatedSchemaResponse, SchemaInsertRequest, InsertedSchema
from utils import datetime_as_string

router = APIRouter()

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client['reservation-system']
collection = db['schemas']


@router.post("/", response_model=CreatedSchemaResponse)
async def create_schema(schema: SchemaInsertRequest):
    existing_schema = await collection.find_one({"name": schema.name})
    if existing_schema:
        raise HTTPException(status_code=400, detail="Schema already exists")

    schema_data = schema.model_dump()
    schema_data['created_at'] = datetime_as_string(datetime.now())# Add created_at field
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
    schema = await collection.find_one({"_id": ObjectId(schema_id)})
    if schema is None:
        raise HTTPException(status_code=404, detail="Schema not found")#

    res_model = InsertedSchema(**schema)
    return res_model


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
