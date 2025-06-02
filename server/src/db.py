from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URI)


# ✅ async generator for dependency injection
async def get_db():
    db = client['reservation-system']
    yield db
