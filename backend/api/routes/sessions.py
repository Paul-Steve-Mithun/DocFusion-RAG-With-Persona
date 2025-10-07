from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from ..routes.auth import get_current_user_id
from ..db.mongo import get_db
from ..core import config
from openai import OpenAI
from ..rag import get_user_chroma_dir
import shutil
import os

router = APIRouter()

@router.get("")
async def list_sessions(user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    out = []
    async for s in db.sessions.find({"owner_id": user_id}).sort("_id", -1):
        out.append({"_id": str(s["_id"]), "name": s.get("name", "New Chat")})
    return out

@router.post("/new")
async def create_session(payload: dict | None = None, user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    requested = (payload or {}).get("name")
    if requested:
        name = requested
    else:
        # Generate sequential Session N based on count, ensuring uniqueness
        count = await db.sessions.count_documents({"owner_id": user_id})
        n = count + 1
        name = f"Session {n}"
        # ensure unique in case of manual naming
        while await db.sessions.find_one({"owner_id": user_id, "name": name}):
            n += 1
            name = f"Session {n}"
    res = await db.sessions.insert_one({"owner_id": user_id, "name": name})
    return {"_id": str(res.inserted_id), "name": name}

@router.patch("/{session_id}/rename")
async def rename_session(session_id: str, payload: dict, user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    try:
        oid = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session id")
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    await db.sessions.update_one({"_id": oid, "owner_id": user_id}, {"$set": {"name": name}})
    return {"_id": session_id, "name": name}

@router.post("/suggest_from_chat")
async def suggest_from_chat(payload: dict, user_id: str = Depends(get_current_user_id)):
    messages = payload.get("messages", [])
    if not messages:
        return {"name": "New Chat"}
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    prompt = (
        "You are titling a chat thread. Given the following last 2-3 exchanges, "
        "produce a short 3-5 word title that captures the topic (no quotes).\n\n"
        + "\n\n".join([f"{m.get('role')}: {m.get('content')}" for m in messages[-6:]])
    )
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.5)
        name = resp.choices[0].message.content.strip().strip('"')
        return {"name": name[:60] or "New Chat"}
    except Exception:
        return {"name": "New Chat"}

@router.delete("/{session_name}")
async def delete_session(session_name: str, user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    # Remove session record
    await db.sessions.delete_many({"owner_id": user_id, "name": session_name})
    # Remove messages
    await db.messages.delete_many({"owner_id": user_id, "session_id": session_name})
    # Remove documents metadata for this session
    await db.documents.delete_many({"owner_id": user_id, "session_id": session_name})
    # Remove per-session Chroma directory
    chroma_dir = get_user_chroma_dir(user_id, session_name)
    try:
        if os.path.isdir(chroma_dir):
            shutil.rmtree(chroma_dir, ignore_errors=True)
    except Exception:
        pass
    return {"status": "deleted"}

@router.post("/rename_by_name")
async def rename_by_name(payload: dict, user_id: str = Depends(get_current_user_id)):
    old_name = (payload or {}).get("old_name")
    new_name = (payload or {}).get("new_name")
    if not old_name or not new_name:
        raise HTTPException(status_code=400, detail="old_name and new_name are required")
    db = await get_db()
    # Update session document (create if missing)
    existing = await db.sessions.find_one({"owner_id": user_id, "name": old_name})
    if existing:
        await db.sessions.update_one({"_id": existing["_id"]}, {"$set": {"name": new_name}})
    else:
        await db.sessions.insert_one({"owner_id": user_id, "name": new_name})
    # Update references - but keep track of original session for fallback purposes
    await db.messages.update_many({"owner_id": user_id, "session_id": old_name}, {"$set": {"session_id": new_name, "original_session_id": old_name}})
    await db.documents.update_many({"owner_id": user_id, "session_id": old_name}, {"$set": {"session_id": new_name, "original_session_id": old_name}})
    # Rename chroma dir if exists and clear vectorstore cache by moving directory
    old_dir = get_user_chroma_dir(user_id, old_name)
    new_dir = get_user_chroma_dir(user_id, new_name)
    try:
        if os.path.isdir(old_dir):
            print(f"Session rename: Moving Chroma directory from '{old_dir}' to '{new_dir}'")
            os.makedirs(os.path.dirname(new_dir), exist_ok=True)
            
            # Copy instead of move to avoid file lock issues with Chroma databases
            import shutil
            try:
                shutil.copytree(old_dir, new_dir, dirs_exist_ok=True)
                print(f"Session rename: Successfully copied Chroma directory to new location")
                
                # Try to remove the old directory after a small delay
                import time
                time.sleep(0.5)  # Give Chroma time to release file locks
                try:
                    shutil.rmtree(old_dir)
                    print(f"Session rename: Successfully removed old Chroma directory")
                except Exception as cleanup_error:
                    print(f"Session rename: Warning - Could not remove old directory (will be cleaned up later): {cleanup_error}")
                    
            except Exception as e:
                print(f"Session rename: Error copying Chroma directory: {e}")
                raise e
        else:
            print(f"Session rename: Old Chroma directory '{old_dir}' does not exist")
    except Exception as e:
        print(f"Session rename: Error moving Chroma directory: {e}")
        import traceback
        traceback.print_exc()
    return {"status": "renamed", "name": new_name}


