#!/usr/bin/env python3
"""
Cleanup script to remove orphaned ChromaDB directories.
Run this script to clean up directories that weren't properly deleted.
"""

import os
import shutil
import asyncio
from api.db.mongo import get_db
from api.rag import get_user_chroma_dir

async def cleanup_orphaned_chroma():
    """Clean up ChromaDB directories that don't have corresponding sessions in MongoDB."""
    
    print("🧹 Starting ChromaDB cleanup...")
    
    # Get all users from MongoDB
    db = await get_db()
    users = set()
    
    # Get all user IDs from sessions
    async for session in db.sessions.find({}):
        users.add(session.get("owner_id"))
    
    # Get all user IDs from documents
    async for doc in db.documents.find({}):
        users.add(doc.get("owner_id"))
    
    print(f"Found {len(users)} users in database")
    
    # Get all active sessions for each user
    user_sessions = {}
    for user_id in users:
        sessions = set()
        async for session in db.sessions.find({"owner_id": user_id}):
            sessions.add(session.get("name"))
        user_sessions[user_id] = sessions
        print(f"User {user_id} has sessions: {list(sessions)}")
    
    # Check ChromaDB directories
    chroma_base_dir = "./chroma_db"
    if not os.path.exists(chroma_base_dir):
        print("No chroma_db directory found")
        return
    
    cleaned_count = 0
    total_size_freed = 0
    
    for user_dir in os.listdir(chroma_base_dir):
        if not user_dir.startswith("user_"):
            continue
            
        user_id = user_dir.replace("user_", "")
        print(f"\nChecking user directory: {user_dir}")
        
        user_path = os.path.join(chroma_base_dir, user_dir)
        if not os.path.isdir(user_path):
            continue
            
        # Get active sessions for this user
        active_sessions = user_sessions.get(user_id, set())
        print(f"Active sessions for user {user_id}: {list(active_sessions)}")
        
        # Check each session directory
        for session_dir in os.listdir(user_path):
            if not session_dir.startswith("session_"):
                continue
                
            session_name = session_dir.replace("session_", "")
            session_path = os.path.join(user_path, session_dir)
            
            if not os.path.isdir(session_path):
                continue
                
            # Check if this session exists in MongoDB
            if session_name not in active_sessions:
                print(f"🗑️  Orphaned session directory found: {session_path}")
                
                # Calculate size before deletion
                try:
                    size = sum(os.path.getsize(os.path.join(dirpath, filename))
                              for dirpath, dirnames, filenames in os.walk(session_path)
                              for filename in filenames)
                    total_size_freed += size
                    print(f"   Size: {size / 1024 / 1024:.2f} MB")
                except:
                    pass
                
                # Delete the directory
                try:
                    shutil.rmtree(session_path)
                    print(f"✅ Deleted: {session_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {session_path}: {e}")
            else:
                print(f"✅ Session directory is active: {session_path}")
    
    print(f"\n🎉 Cleanup complete!")
    print(f"📊 Directories cleaned: {cleaned_count}")
    print(f"💾 Space freed: {total_size_freed / 1024 / 1024:.2f} MB")

async def main():
    """Main function to run the cleanup."""
    try:
        await cleanup_orphaned_chroma()
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 ChromaDB Orphaned Directories Cleanup Tool")
    print("=" * 50)
    asyncio.run(main())
