from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, documents, chat, sessions
from .db.mongo import ensure_indexes

app = FastAPI(title="Persona RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    print("✓ Server started - embedding model will load on first document upload")


