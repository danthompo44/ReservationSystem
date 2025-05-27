from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

client = AsyncIOMotorClient('mongodb://mongodb:27017')
db = client['reservation-system']
objects_collection = db['objects']
schemas_collection = db['schemas']  # Collection for schemas

@router.post("/")
async def create_object(object_data: dict):
    schema_id = object_data.get("schema_id")
    schema = await schemas_collection.find_one({"_id": ObjectId(schema_id)})

    if schema is None:
        raise HTTPException(status_code=400, detail="Schema not found")

    # Validate object data against schema
    for key in schema.keys():
        if key != "_id" and key != "created_at" and key not in object_data:
            raise HTTPException(status_code=400, detail=f"Missing field: {key}")

    object_data['created_at'] = datetime.now()  # Add created_at field
    result = await objects_collection.insert_one(object_data)
    return {
        "_id": str(result.inserted_id),
        "message": "Object created successfully",
        "data": object_data
    }


@router.get("/")
async def read_objects():
    objects = []
    async for obj in objects_collection.find():
        objects.append({**obj, "_id": str(obj["_id"])})  # Correctly format object
    return objects


@router.get("/{object_id}", response_model=dict)
async def read_object(object_id: str):
    obj = await objects_collection.find_one({"_id": ObjectId(object_id)})
    if obj is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {**obj, "_id": str(obj["_id"])}


@router.put("/{object_id}", response_model=dict)
async def update_object(object_id: str, object_data: dict):
    result = await objects_collection.update_one({"_id": ObjectId(object_id)}, {"$set": object_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")
    return {**object_data, "_id": object_id}


@router.delete("/{object_id}")
async def delete_object(object_id: str):
    result = await objects_collection.delete_one({"_id": ObjectId(object_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")
    return {"detail": "Object deleted"}
