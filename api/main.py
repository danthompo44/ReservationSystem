from typing import List, Callable, Union
from datetime import datetime
from functools import wraps

import uvicorn
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from basemodels import ObjectSchema
from routes.schemarouter import router as schema_router
from routes.reservationrouter import router as reservation_router  # Import the reservation router
from routes.objectrouter import router as object_router  # Import the object router
from routes.topologyrouter import router as topology_router  # Import the topology router

app = FastAPI()

client = AsyncIOMotorClient('mongodb://mongodb:27017')
db = client['reservation-system']
collection = db['schemas']
objects_collection = db['objects']
topologies_collection = db['topologies']  # New collection for topologies
reservations_collection = db['reservations']  # New collection for reservations


def serialise_res(res: Union[dict, list]):
    if isinstance(res, dict):
        result = {}
        for k, v in res.items():
            if isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, dict):
                result[k] = serialise_res(v)
            elif isinstance(v, list):
                result[k] = [serialise_res(i) if isinstance(i, dict) else i for i in v]
            else:
                result[k] = v

    elif isinstance(res, list):
        result = []

        for obj in res:
            result.append(serialise_res(obj))
    else:
        result = None

    return result


def serialise_response(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        return serialise_res(response)
    return wrapper


# Include the routers
app.include_router(schema_router, prefix="/schemas", tags=["schemas"])
app.include_router(reservation_router, prefix="/reservations", tags=["reservations"])
app.include_router(object_router, prefix="/objects", tags=["objects"])
app.include_router(topology_router, prefix="/topologies", tags=["topologies"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
