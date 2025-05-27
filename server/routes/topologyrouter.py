from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

client = AsyncIOMotorClient('mongodb://mongodb:27017')
db = client['reservation-system']
topologies_collection = db['topologies']


@router.post("/")
async def create_topology(topology_data: dict):
    topology_data['created_at'] = datetime.now()  # Add created_at field
    result = await topologies_collection.insert_one(topology_data)
    return {
        "_id": str(result.inserted_id),
        "message": "Topology created successfully",
        "data": topology_data
    }


@router.get("/")
async def read_topologies():
    topologies = []
    async for topology in topologies_collection.find():
        topologies.append({**topology, "_id": str(topology["_id"])})  # Correctly format topology
    return topologies


@router.get("/{topology_id}")
async def read_topology(topology_id: str):
    topology = await topologies_collection.find_one({"_id": ObjectId(topology_id)})
    if topology is None:
        raise HTTPException(status_code=404, detail="Topology not found")
    return {**topology, "_id": str(topology["_id"])}


@router.put("/{topology_id}")
async def update_topology(topology_id: str, topology_data: dict):
    result = await topologies_collection.update_one({"_id": ObjectId(topology_id)}, {"$set": topology_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Topology not found")
    return {**topology_data, "_id": topology_id}


@router.delete("/{topology_id}")
async def delete_topology(topology_id: str):
    result = await topologies_collection.delete_one({"_id": ObjectId(topology_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topology not found")
    return {"detail": "Topology deleted"}
