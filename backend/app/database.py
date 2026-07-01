import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db = None


def get_client() -> AsyncIOMotorClient:
    """Get the MongoDB client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_db():
    """Get the MongoDB database."""
    global _db
    if _db is None:
        client = get_client()
        _db = client[settings.mongodb_db_name]
    return _db


async def get_users_collection():
    """Get the users collection."""
    db = get_db()
    return db["users"]


async def get_detections_collection():
    """Get the detections collection."""
    db = get_db()
    return db["detections"]


async def get_settings_collection():
    """Get the settings collection."""
    db = get_db()
    return db["settings"]


async def get_activities_collection():
    """Get the activity_logs collection."""
    db = get_db()
    return db["activity_logs"]


async def connect_db():
    """Connect to MongoDB and ensure indexes."""
    try:
        client = get_client()
        # Ping the database to verify connection
        await client.admin.command("ping")
        db = get_db()

        # Ensure indexes
        users = await get_users_collection()
        # Drop and recreate email index to add sparse=True if needed
        try:
            await users.create_index("email", unique=True, sparse=True)
        except Exception:
            # Index may already exist without sparse — drop and retry
            await users.drop_index("email_1")
            await users.create_index("email", unique=True, sparse=True)
        await users.create_index("username", unique=True)

        detections = await get_detections_collection()
        await detections.create_index("user_id")
        await detections.create_index([("user_id", 1), ("created_at", -1)])

        # Ensure activity_logs indexes
        activities = await get_activities_collection()
        await activities.create_index([("created_at", -1)])
        await activities.create_index([("method", 1), ("created_at", -1)])
        await activities.create_index([("status_code", 1), ("created_at", -1)])
        await activities.create_index("user_id")
        # TTL index: auto-delete logs older than 90 days
        await activities.create_index(
            "created_at",
            expireAfterSeconds=90 * 24 * 3600,
        )

        # Ensure settings collection exists with default
        settings_col = await get_settings_collection()
        existing = await settings_col.find_one({"_id": "global_config"})
        if existing is None:
            from app.config import settings as app_cfg
            await settings_col.insert_one({
                "_id": "global_config",
                "app_name": app_cfg.app_name,
                "image_model_mode": "auto",
            })

        logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")
