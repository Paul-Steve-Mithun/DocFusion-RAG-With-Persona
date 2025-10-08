# DocFusion Deployment Guide for Render

This guide covers two deployment approaches for your DocFusion application on Render.

---

## Option 1: Two Separate Services (RECOMMENDED)

This approach deploys backend and frontend as separate services, which is more scalable and follows best practices.

### Step 1: Deploy Backend API

1. **Go to Render Dashboard** → New → Web Service
2. **Connect your GitHub repository**
3. **Configure the Backend Service:**
   - **Name**: `docfusion-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or your preferred tier)

4. **Add Environment Variables** (in Render dashboard):
   ```
   GROQ_API_KEY=your_groq_api_key
   HUGGINGFACE_TOKEN=your_huggingface_token
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URL=your_mongodb_connection_string
   JWT_SECRET_KEY=your_secret_key_for_jwt
   CLOUDINARY_CLOUD_NAME=your_cloudinary_name
   CLOUDINARY_API_KEY=your_cloudinary_key
   CLOUDINARY_API_SECRET=your_cloudinary_secret
   ```

5. **Deploy** and note your backend URL (e.g., `https://docfusion-backend.onrender.com`)

### Step 2: Deploy Frontend Static Site

1. **Go to Render Dashboard** → New → Static Site
2. **Connect your GitHub repository**
3. **Configure the Frontend Service:**
   - **Name**: `docfusion-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Add Environment Variable:**
   ```
   VITE_API_URL=https://docfusion-backend.onrender.com
   ```
   *(Replace with your actual backend URL from Step 1)*

5. **Deploy**

### Step 3: Update CORS (Important!)

Update your backend's CORS settings to allow your frontend domain:

Edit `backend/api/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://docfusion-frontend.onrender.com",  # Add your frontend URL
        "http://localhost:5173",  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy the backend after this change.

---

## Option 2: Single Service (Backend Serves Frontend)

This approach builds the frontend and serves it from the FastAPI backend.

### Step 1: Update Backend to Serve Static Files

Edit `backend/api/server.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
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

# API routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Serve static files from frontend build
static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # For client-side routing, return index.html
        return FileResponse(static_dir / "index.html")

@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
```

### Step 2: Update Frontend Configuration

Create `frontend/.env.production`:
```
VITE_API_URL=/api
```

### Step 3: Deploy on Render

1. **Go to Render Dashboard** → New → Web Service
2. **Configure:**
   - **Root Directory**: `DocFusion` (or leave blank if DocFusion is root)
   - **Build Command**: 
     ```bash
     cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd backend && uvicorn api.server:app --host 0.0.0.0 --port $PORT
     ```

3. **Add all environment variables** (same as Option 1 backend)

---

## Using render.yaml (Blueprint)

Alternatively, use the provided `render.yaml` file for automatic deployment:

1. Push the `render.yaml` file to your repository
2. Go to Render Dashboard → New → Blueprint
3. Connect your repository
4. Render will automatically create both services
5. Add the required environment variables to each service

---

## Local Development

For local development, the proxy setup in `vite.config.js` still works:

1. **Terminal 1 (Backend):**
   ```bash
   cd backend
   uvicorn api.server:app --reload
   ```

2. **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm run dev
   ```

The frontend will proxy `/api` calls to `http://localhost:8000`.

---

## Troubleshooting

### Backend won't start
- Check that all environment variables are set
- Verify MongoDB connection string is correct
- Check Render logs for Python errors

### Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Check browser console for CORS errors

### 404 errors on frontend routes
- Ensure the catch-all route is properly configured (Option 2)
- For static sites (Option 1), configure rewrite rules in Render

---

## Recommended Approach

**Option 1 (Two Separate Services)** is recommended because:
- ✅ Better separation of concerns
- ✅ Independent scaling
- ✅ Easier debugging
- ✅ Frontend can be deployed to CDN
- ✅ Faster rebuilds (only rebuild what changed)

