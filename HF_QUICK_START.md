# 🚀 Hugging Face Spaces - Quick Start

## ⚡ Super Fast Deployment Guide

### 1️⃣ Create Space (2 minutes)
1. Go to https://huggingface.co/new-space
2. Name: `docfusion-backend`
3. SDK: **Docker** ⚠️
4. Hardware: **CPU basic** (FREE)
5. Visibility: **Public**
6. Click **Create**

---

### 2️⃣ Upload Files (5 minutes)

**Click "Files" → "Upload files" and upload:**

From `DocFusion/backend/` folder:
- ✅ Entire `api/` folder
- ✅ `requirements.txt`
- ✅ `Dockerfile` (the new one)

Rename:
- ✅ `README_HF.md` → `README.md`

---

### 3️⃣ Add Secrets (3 minutes)

**Settings → Repository secrets → Add these:**

```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/docfusion
JWT_SECRET_KEY=generate-a-random-string-here
OPENAI_API_KEY=sk-your-openai-key
HUGGINGFACE_TOKEN=hf_your-token
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
```

Optional:
```
GROQ_API_KEY=your-groq-key
```

---

### 4️⃣ Wait for Build (10 minutes first time)

Watch **"Logs"** tab:
- Installing dependencies... ⏳
- Downloading model... ⏳
- Server starting... ⏳
- ✅ **Running!**

---

### 5️⃣ Test Backend (1 minute)

Your API: `https://YOUR_USERNAME-docfusion-backend.hf.space`

Test: `https://YOUR_USERNAME-docfusion-backend.hf.space/api/health`

Should see: `{"status":"ok"}` ✅

---

### 6️⃣ Deploy Frontend to Vercel (5 minutes)

1. Go to https://vercel.com
2. Import your GitHub repo
3. **Root Directory**: `frontend`
4. **Framework**: Vite
5. Add env var:
   ```
   VITE_API_URL=https://YOUR_USERNAME-docfusion-backend.hf.space/api
   ```
6. **Deploy!**

---

### 7️⃣ Update CORS (2 minutes)

In your HF Space, edit `api/server.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app",  # Your Vercel URL
]
```

Save → Auto-redeploys ✅

---

### 8️⃣ Test Everything! 🎉

1. Visit your Vercel URL
2. Register account
3. Upload PDF
4. Chat with it!

---

## 🎯 Total Time: ~30 minutes

## 💰 Total Cost: **$0 (FREE!)**

## 📊 What You Get:

- ✅ 2GB RAM backend (HF Spaces)
- ✅ Fast frontend (Vercel CDN)
- ✅ Always-on (no spin-down)
- ✅ Persistent model caching
- ✅ Great for portfolio
- ✅ Public project showcase

---

## 🆘 Quick Troubleshooting

**Space won't start?**
- Check Logs tab for errors
- Verify all secrets are set

**CORS error?**
- Update `allow_origins` with Vercel URL

**Slow first upload?**
- Normal! Model downloads on first use
- Takes 5-10 min first time
- Fast after that

---

## 📚 Full Guide

See `HF_SPACES_DEPLOYMENT.md` for detailed instructions.

---

**Ready? Let's deploy!** 🚀
