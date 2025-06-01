from typing import List, Annotated
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body, Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from basemodels.object_base_models import CreateObjectResponse, CreateObjectRequest
from db import db
from utils import build_pydantic_model

router = APIRouter()

objects_collection = db['objects']
schemas_collection = db['schemas']  # Collection for schemas

@router.post("/", response_model=CreateObjectResponse, response_model_exclude_none=True)
async def create_object(
        data: CreateObjectRequest
):
    schema = await schemas_collection.find_one({"_id": data.schema_id})

    if schema is None:
        raise HTTPException(status_code=400, detail="Schema not found")

    schema_model = build_pydantic_model(schema.get("schema_name"), schema.get("fields"))
    try:
        schema_model(**data.fields)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid object data: {e}"
        )

    now = datetime.now()
    body = data.model_dump(exclude_unset=True, exclude_none=True)
    body["created_at"] = now
    body["updated_at"] = now

    result = await objects_collection.insert_one(body)

    res = {
        "_id": result.inserted_id,
        "message": "Object created successfully",
        "data": body
    }

    res = CreateObjectResponse(**res)
    return res


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
