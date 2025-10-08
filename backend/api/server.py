from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, documents, chat, sessions
from .db.mongo import ensure_indexes

app = FastAPI(title="Persona RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "https://docfusion-backend.onrender.com",
        # Add your frontend URL when deployed:
        # "https://your-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    # Pre-download embedding model to avoid timeout on first document upload
    try:
        print("Pre-loading embedding model...")
        from .rag import get_embeddings
        embeddings = get_embeddings()
        # Test the model to ensure it's fully loaded
        embeddings.embed_query("test")
        print("✓ Embedding model loaded successfully")
    except Exception as e:
        print(f"Warning: Failed to pre-load embedding model: {e}")
        print("Model will be downloaded on first document upload")


