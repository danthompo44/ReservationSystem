import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.routes.objectrouter import router as object_router  # Import the object router
from src.routes.schemarouter import router as schema_router

app = FastAPI()

client = AsyncIOMotorClient('mongodb://mongodb:27017')
db = client['reservation-system']
collection = db['schemas']
objects_collection = db['objects']
topologies_collection = db['topologies']  # New collection for topologies
reservations_collection = db['reservations']  # New collection for reservations

# Include the routers
app.include_router(schema_router, prefix="/schemas", tags=["schemas"])
app.include_router(object_router, prefix="/objects", tags=["objects"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
