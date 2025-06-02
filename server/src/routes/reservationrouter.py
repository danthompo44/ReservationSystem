from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from src.db import get_db

router = APIRouter()

db = get_db()
reservations_collection = db['reservations']
topologies_collection = db['topologies']  # New collection for topologies


@router.post("/")
async def reserve_topology(reservation_data: dict):
    topology_id = reservation_data.get("topology_id")
    topology = await topologies_collection.find_one({"_id": ObjectId(topology_id)})

    if topology is None:
        raise HTTPException(status_code=400, detail="Topology not found")

    reservation_data['created_at'] = datetime.now()  # Add created_at field
    result = await reservations_collection.insert_one(reservation_data)
    return {
        "_id": str(result.inserted_id),
        "message": "Topology reserved successfully",
        "data": reservation_data
    }


@router.get("/")
async def read_reservations():
    reservations = []
    async for reservation in reservations_collection.find():
        reservations.append({**reservation, "_id": str(reservation["_id"])})  # Correctly format reservation
    return reservations
