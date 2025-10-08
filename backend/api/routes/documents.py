import os
import tempfile
import requests
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import Response
from ..routes.auth import get_current_user_id
from ..db.mongo import get_db
from bson import ObjectId
from ..rag import index_pdf_for_user
from ..core import config
from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url

router = APIRouter()

# Configure Cloudinary
cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id), session_id: str | None = Form(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    db = await get_db()
    content = await file.read()
    
    # Insert document record first to get the ID
    doc = {"owner_id": user_id, "session_id": session_id or "", "filename": file.filename, "size": len(content)}
    res = await db.documents.insert_one(doc)
    doc_id = str(res.inserted_id)
    
    # Create temp file for indexing and Cloudinary upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        temp_path = tmp.name
    
    try:
        # Upload to Cloudinary
        # Use user_id and doc_id in the public_id for organization and security
        cloudinary_response = cloudinary.uploader.upload(
            temp_path,
            resource_type="raw",  # 'raw' type for PDFs
            public_id=f"docfusion/{user_id}/{doc_id}",
            folder="docfusion_pdfs",
            overwrite=True,
            tags=[user_id, session_id or "no_session"]
        )
        
        cloudinary_url = cloudinary_response.get("secure_url")
        cloudinary_public_id = cloudinary_response.get("public_id")
        
        # Update document record with Cloudinary URL
        await db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"cloudinary_url": cloudinary_url, "cloudinary_public_id": cloudinary_public_id}}
        )
        
        # Index PDF for RAG
        index_pdf_for_user(user_id, temp_path, session_id=session_id)
        
    except ValueError as e:
        # Clean up if indexing fails
        try:
            # Try to delete from Cloudinary if it was uploaded
            if 'cloudinary_public_id' in locals():
                cloudinary.uploader.destroy(cloudinary_public_id, resource_type="raw")
        except:
            pass
        await db.documents.delete_one({"_id": ObjectId(doc_id)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Clean up on any error
        await db.documents.delete_one({"_id": ObjectId(doc_id)})
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
    
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

@router.get("/test-cloudinary")
async def test_cloudinary():
    """Test endpoint to verify Cloudinary configuration"""
    try:
        # Test Cloudinary configuration
        config_status = {
            "cloud_name": bool(config.CLOUDINARY_CLOUD_NAME),
            "api_key": bool(config.CLOUDINARY_API_KEY),
            "api_secret": bool(config.CLOUDINARY_API_SECRET)
        }
        
        # Test Cloudinary connection
        test_result = cloudinary.api.ping()
        
        return {
            "status": "success",
            "config": config_status,
            "cloudinary_ping": test_result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "config": {
                "cloud_name": bool(config.CLOUDINARY_CLOUD_NAME),
                "api_key": bool(config.CLOUDINARY_API_KEY),
                "api_secret": bool(config.CLOUDINARY_API_SECRET)
            }
        }

@router.get("/{document_id}/view")
async def view_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    """Fetch PDF from Cloudinary and serve it to the browser"""
    db = await get_db()
    
    # Verify document exists and belongs to user
    try:
        doc = await db.documents.find_one({"_id": ObjectId(document_id), "owner_id": user_id})
    except:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get Cloudinary public_id from document
    cloudinary_public_id = doc.get("cloudinary_public_id")
    
    if not cloudinary_public_id:
        # This document was uploaded before Cloudinary integration
        # Check if it has a cloudinary_url as fallback
        doc_cloudinary_url = doc.get("cloudinary_url")
        if doc_cloudinary_url:
            # Extract public_id from URL
            try:
                # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/docfusion/user_id/doc_id.pdf
                parts = doc_cloudinary_url.split('/')
                if 'docfusion' in parts:
                    # Find the docfusion part and reconstruct public_id
                    docfusion_index = parts.index('docfusion')
                    public_id_parts = parts[docfusion_index:]
                    cloudinary_public_id = '/'.join(public_id_parts).replace('.pdf', '')
                else:
                    raise HTTPException(status_code=404, detail="PDF file not found in cloud storage")
            except:
                raise HTTPException(status_code=404, detail="PDF file not found in cloud storage")
        else:
            # Document was uploaded before Cloudinary integration
            # Return a helpful error message
            raise HTTPException(
                status_code=404, 
                detail="This document was uploaded before cloud storage integration. Please re-upload it to view."
            )
    
    try:
        # Use Cloudinary's admin API to download the file directly
        # This works even when PDF delivery is disabled on free accounts
        import cloudinary.api
        
        # Get the resource using admin API
        resource_info = cloudinary.api.resource(
            cloudinary_public_id,
            resource_type="raw"
        )
        
        # Get the secure URL from the resource info
        secure_url = resource_info.get('secure_url')
        if not secure_url:
            raise HTTPException(status_code=404, detail="PDF file not found in cloud storage")
        
        # Download the file using the secure URL
        response = requests.get(secure_url, timeout=30)
        
        if response.status_code != 200:
            # If direct URL fails, try using the admin API to download the file content
            try:
                # Use admin API to get the file content directly
                file_content = cloudinary.uploader.download(cloudinary_public_id, resource_type="raw")
                
                return Response(
                    content=file_content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'inline; filename="{doc.get("filename", "document.pdf")}"',
                        "Cache-Control": "public, max-age=3600"
                    }
                )
            except Exception as download_error:
                raise HTTPException(status_code=404, detail="Failed to retrieve PDF from cloud storage")
        
        # Return the PDF with proper headers for inline viewing
        return Response(
            content=response.content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{doc.get("filename", "document.pdf")}"',
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

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


