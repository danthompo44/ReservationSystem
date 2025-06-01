import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from server.routes.objectrouter import router as object_router  # Import the object router
from server.routes.reservationrouter import router as reservation_router  # Import the reservation router
from server.routes.schemarouter import router as schema_router
from server.routes.topologyrouter import router as topology_router  # Import the topology router

app = FastAPI()

client = AsyncIOMotorClient('mongodb://mongodb:27017')
db = client['reservation-system']
collection = db['schemas']
objects_collection = db['objects']
topologies_collection = db['topologies']  # New collection for topologies
reservations_collection = db['reservations']  # New collection for reservations

# Include the routers
app.include_router(schema_router, prefix="/schemas", tags=["schemas"])
app.include_router(reservation_router, prefix="/reservations", tags=["reservations"])
app.include_router(object_router, prefix="/objects", tags=["objects"])
app.include_router(topology_router, prefix="/topologies", tags=["topologies"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
