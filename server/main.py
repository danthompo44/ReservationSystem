import uvicorn
from fastapi import FastAPI

from src.routes.objectrouter import router as object_router  # Import the object router
from src.routes.schemarouter import router as schema_router

app = FastAPI()

# Include the routers
app.include_router(schema_router, prefix="/schemas", tags=["schemas"])
app.include_router(object_router, prefix="/objects", tags=["objects"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
