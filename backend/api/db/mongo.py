from motor.motor_asyncio import AsyncIOMotorClient
from ..core import config

client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(config.MONGODB_URI)
    return client

async def get_db():
    return get_client().get_default_database()

async def ensure_indexes():
    db = await get_db()
    # Users: unique email
    await db.users.create_index("email", unique=True)
    # Documents: owner_id for quick lookups
    await db.documents.create_index("owner_id")
    # Sessions: owner_id + name
    await db.sessions.create_index([("owner_id", 1), ("name", 1)], unique=True)
    # Messages: owner_id + session_id ordered by time
    await db.messages.create_index([("owner_id", 1), ("session_id", 1), ("ts", 1)])


