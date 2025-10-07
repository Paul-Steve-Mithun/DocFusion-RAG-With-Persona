import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from ..routes.auth import get_current_user_id
from ..db.mongo import get_db
from bson import ObjectId
from ..rag import index_pdf_for_user
from ..core import config
from openai import OpenAI

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id), session_id: str | None = Form(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    db = await get_db()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name
    try:
        index_pdf_for_user(user_id, temp_path, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
    doc = {"owner_id": user_id, "session_id": session_id or "", "filename": file.filename, "size": len(content)}
    res = await db.documents.insert_one(doc)
    doc_id = str(res.inserted_id)
    # Build response explicitly to avoid leaking ObjectId from mutated doc
    return {"_id": doc_id, "owner_id": user_id, "filename": file.filename, "size": len(content)}

@router.get("")
async def list_documents(user_id: str = Depends(get_current_user_id), session_id: str | None = None):
    db = await get_db()
    docs = []
    query = {"owner_id": user_id}
    if session_id is not None:
        query["session_id"] = session_id
    async for d in db.documents.find(query).sort("_id", -1):
        d["_id"] = str(d["_id"])
        docs.append(d)
    return docs

@router.post("/reembed_all")
async def reembed_all(user_id: str = Depends(get_current_user_id)):
    """Clear all Chroma databases for the current user to force re-indexing with new embedding model."""
    from ..rag import get_user_chroma_dir
    import shutil
    import os
    
    # Clear all user's Chroma data
    user_base_dir = get_user_chroma_dir(user_id, None)
    try:
        if os.path.exists(user_base_dir):
            shutil.rmtree(user_base_dir)
            print(f"Cleared Chroma database for user {user_id}")
    except Exception as e:
        print(f"Error clearing Chroma database: {e}")
    
    return {"status": "cleared", "message": "All Chroma databases cleared. Please re-upload your PDFs to re-index with the new embedding model."}

@router.post("/suggest_session_name")
async def suggest_session_name(user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    titles = []
    async for d in db.documents.find({"owner_id": user_id}).sort("_id", -1).limit(5):
        titles.append(d.get("filename", ""))
    if not titles:
        return {"name": "New Chat"}
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    prompt = "Generate a short, 3-5 word session name summarizing these PDFs: " + ", ".join(titles)
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.5)
        name = resp.choices[0].message.content.strip().strip('"')
        return {"name": name[:60] or "New Chat"}
    except Exception:
        return {"name": "New Chat"}


