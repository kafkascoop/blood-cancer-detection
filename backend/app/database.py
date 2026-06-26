from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None


async def get_database():
    """Get the MongoDB database instance."""
    if client is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return client[settings.mongodb_db_name]


async def connect_db():
    """Initialize the MongoDB connection."""
    global client
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.detections.create_index([("user_id", 1), ("created_at", -1)])
    await db.detections.create_index([("user_id", 1), ("patient_name", "text")])

    print(f"Connected to MongoDB: {settings.mongodb_db_name}")
    return db


async def close_db():
    """Close the MongoDB connection."""
    global client
    if client:
        client.close()
        client = None
        print("MongoDB connection closed")


async def get_users_collection():
    db = await get_database()
    return db["users"]


async def get_detections_collection():
    db = await get_database()
    return db["detections"]
