# 🚀 Quick Start: Deploy DocFusion on Render

## TL;DR - Fastest Way to Deploy

### Option A: Two Separate Services (Recommended ⭐)

#### 1️⃣ Deploy Backend First
```
Service Type: Web Service
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn api.server:app --host 0.0.0.0 --port $PORT
Runtime: Python 3
```

**Environment Variables to Add:**
- `MONGODB_URL` - Your MongoDB connection string
- `JWT_SECRET_KEY` - Random secure string
- `GROQ_API_KEY` - Your Groq API key
- `HUGGINGFACE_TOKEN` - Your HuggingFace token
- `OPENAI_API_KEY` - Your OpenAI key
- `CLOUDINARY_CLOUD_NAME` - Cloudinary name
- `CLOUDINARY_API_KEY` - Cloudinary key
- `CLOUDINARY_API_SECRET` - Cloudinary secret

**Copy your backend URL:** `https://your-backend-name.onrender.com`

#### 2️⃣ Deploy Frontend
```
Service Type: Static Site
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

**Environment Variables to Add:**
- `VITE_API_URL` = `https://your-backend-name.onrender.com` (from step 1)

#### 3️⃣ Update Backend CORS
Edit `backend/api/server.py`, line 10-14:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-name.onrender.com",  # Add your frontend URL
        "http://localhost:5173",  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push changes to redeploy backend.

**✅ Done!** Visit your frontend URL.

---

## Your Code Changes Summary

I've updated your codebase with:

1. ✅ **`frontend/src/api/client.js`** - Now uses environment variable for API URL
2. ✅ **`render.yaml`** - Blueprint for automatic deployment (optional)
3. ✅ **`frontend/env.example`** - Template for environment variables
4. ✅ **`backend/env.example`** - Template for backend environment variables
5. ✅ **`DEPLOYMENT_GUIDE.md`** - Comprehensive deployment guide

---

## Current Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Frontend      │  HTTPS  │    Backend       │
│   (React)       │────────>│   (FastAPI)      │
│   Static Site   │         │   Web Service    │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │    MongoDB       │
                            │    (Database)    │
                            └──────────────────┘
```

**Development:**
- Frontend: `http://localhost:5173` (proxies to backend)
- Backend: `http://localhost:8000`

**Production (Render):**
- Frontend: `https://your-app.onrender.com` (static site)
- Backend: `https://your-api.onrender.com` (web service)

---

## Next Steps

1. **Create Render account** at https://render.com
2. **Connect your GitHub repository**
3. **Follow Option A above** (or use the detailed `DEPLOYMENT_GUIDE.md`)
4. **Set up MongoDB Atlas** if you haven't (free tier available)
5. **Get your API keys** (Groq, HuggingFace, OpenAI, Cloudinary)

---

## Important Notes

⚠️ **Free Tier Considerations:**
- Backend spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds
- Consider paid tier for production use

📝 **Before Deploying:**
- Update `.gitignore` to never commit `.env` files
- Use strong, random JWT_SECRET_KEY
- Keep API keys secure in Render environment variables

🔧 **Troubleshooting:**
- Check Render logs if service fails
- Verify all environment variables are set
- Test backend `/api/health` endpoint first
- Check browser console for CORS errors

---

## Support

See `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.

