"""
Quick script to clean up duplicate sessions in MongoDB
Run this if you encounter duplicate key errors
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/persona_rag")

async def cleanup_duplicate_sessions():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.get_default_database()
    
    print("🔍 Checking for duplicate sessions...")
    
    # Get all sessions
    sessions = []
    async for session in db.sessions.find():
        sessions.append(session)
    
    print(f"Found {len(sessions)} total sessions")
    
    # Group by owner_id and name
    seen = {}
    duplicates_to_delete = []
    
    for session in sessions:
        owner_id = session.get("owner_id")
        name = session.get("name")
        key = f"{owner_id}_{name}"
        
        if key in seen:
            # This is a duplicate - mark for deletion
            duplicates_to_delete.append(session["_id"])
            print(f"❌ Duplicate found: {name} for user {owner_id}")
        else:
            seen[key] = session["_id"]
    
    if duplicates_to_delete:
        print(f"\n🗑️  Deleting {len(duplicates_to_delete)} duplicate sessions...")
        result = await db.sessions.delete_many({"_id": {"$in": duplicates_to_delete}})
        print(f"✅ Deleted {result.deleted_count} duplicate sessions")
    else:
        print("✅ No duplicates found!")
    
    client.close()
    print("\n✨ Cleanup complete!")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_sessions())

