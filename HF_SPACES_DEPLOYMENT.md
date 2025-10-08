# 🤗 Deploying DocFusion Backend to Hugging Face Spaces

## Why Hugging Face Spaces?

✅ **2GB RAM** - 4x more than Render free tier  
✅ **FREE** for public projects  
✅ **Perfect for ML/AI** - designed for this!  
✅ **Persistent storage** - models stay cached  
✅ **No spin-down** - always on  
✅ **Great for portfolios** - public showcase  

---

## 📋 Prerequisites

1. **Hugging Face Account** - Sign up at https://huggingface.co
2. **MongoDB Atlas** - Free cluster at https://mongodb.com/atlas
3. **Cloudinary Account** - Free at https://cloudinary.com
4. **API Keys** - OpenAI, Groq, HuggingFace token

---

## 🚀 Deployment Steps

### Step 1: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in details:
   - **Space name**: `docfusion-backend` (or your choice)
   - **License**: MIT
   - **Select SDK**: **Docker** ⚠️ Important!
   - **Space hardware**: CPU basic (FREE)
   - **Visibility**: Public

4. Click **"Create Space"**

---

### Step 2: Upload Your Code

You have two options:

#### **Option A: Git Push (Recommended)**

```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/docfusion-backend
cd docfusion-backend

# Copy backend files
cp -r ../DocFusion/backend/* .

# Copy the Dockerfile and README
cp ../DocFusion/backend/Dockerfile .
cp ../DocFusion/backend/README_HF.md README.md

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### **Option B: Web Interface (Easier)**

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from `DocFusion/backend/`:
   - All files in `api/` folder
   - `requirements.txt`
   - `Dockerfile` (the new one I created)
   - `README_HF.md` (rename to `README.md`)

---

### Step 3: Configure Environment Variables

1. In your Space, click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add these secrets (one by one):

```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/docfusion
JWT_SECRET_KEY=your-random-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key
GROQ_API_KEY=your-groq-api-key (optional)
HUGGINGFACE_TOKEN=hf_your-huggingface-token
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-secret
```

**Important**: Click "Add secret" for EACH variable!

---

### Step 4: Wait for Build

1. Space will automatically build (5-10 minutes first time)
2. Watch the **"Logs"** tab for progress
3. Look for: `INFO: Uvicorn running on...`
4. When done, you'll see **"Running"** status ✅

---

### Step 5: Test Your API

Your backend will be at:
```
https://YOUR_USERNAME-docfusion-backend.hf.space
```

Test the health endpoint:
```
https://YOUR_USERNAME-docfusion-backend.hf.space/api/health
```

Should return: `{"status":"ok"}` ✅

---

## 🌐 Deploy Frontend to Vercel

Now deploy your React frontend to Vercel (FREE):

### Step 1: Prepare Frontend

1. Update `DocFusion/frontend/.env`:
   ```
   VITE_API_URL=https://YOUR_USERNAME-docfusion-backend.hf.space/api
   ```

2. Commit the change:
   ```bash
   cd DocFusion
   git add frontend/.env
   git commit -m "Update API URL for HF Spaces"
   git push
   ```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click **"Add New Project"**
4. Import your `DocFusion` repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add environment variable:
   - `VITE_API_URL` = `https://YOUR_USERNAME-docfusion-backend.hf.space/api`
7. Click **"Deploy"**

---

## 🔧 Update CORS

After deploying frontend, update your backend CORS:

1. Edit `backend/api/server.py` on Hugging Face:
   ```python
   allow_origins=[
       "http://localhost:5173",
       "https://your-frontend.vercel.app",  # Add your Vercel URL
   ]
   ```

2. Commit the change (Space will auto-redeploy)

---

## ✅ Final Testing

1. Visit your Vercel frontend URL
2. Register a new account
3. Login
4. Create a session
5. Upload a PDF document
6. Chat with it!

---

## 📊 What You Get

### Backend (Hugging Face)
- **URL**: `https://YOUR_USERNAME-docfusion-backend.hf.space`
- **RAM**: 2GB (FREE)
- **Uptime**: Always on
- **Storage**: Persistent (models cached)
- **Cost**: $0/month

### Frontend (Vercel)
- **URL**: `https://your-app.vercel.app`
- **Bandwidth**: Unlimited
- **CDN**: Global
- **SSL**: Free
- **Cost**: $0/month

### Total Cost: **FREE!** 🎉

---

## 🐛 Troubleshooting

### Space won't start
- Check **Logs** tab for errors
- Verify all environment variables are set
- Make sure Dockerfile is in root of Space

### CORS errors
- Update `allow_origins` in `backend/api/server.py`
- Include your Vercel URL

### Model download slow
- First startup takes 5-10 minutes (downloads model)
- Subsequent starts are much faster (model cached)

### MongoDB connection fails
- Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Verify connection string format

---

## 🎯 Advantages Over Render

| Feature | Render Free | HF Spaces |
|---------|-------------|-----------|
| RAM | 512 MB ❌ | 2 GB ✅ |
| Spin-down | After 15 min | Never |
| Model caching | Ephemeral | Persistent ✅ |
| Reliability | Poor | Excellent ✅ |
| ML-optimized | No | Yes ✅ |
| Cost | $0 | $0 |

---

## 📝 Notes

- Your app will be **publicly visible** on Hugging Face
- Great for **portfolio/showcase** projects
- If you need private hosting later, upgrade to HF Pro ($9/month)
- Vercel frontend can be private on free tier

---

## 🎉 You're Done!

Your RAG application is now:
- ✅ Deployed and working
- ✅ Completely free
- ✅ Much more reliable than Render
- ✅ Great for your portfolio

**Share your Space URL and show off your project!** 🚀
