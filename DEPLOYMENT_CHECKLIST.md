# 🚀 Render Deployment Checklist

Use this checklist to ensure a smooth deployment to Render.

---

## Pre-Deployment Setup

### 1. External Services Setup

#### MongoDB Atlas (Database)
- [ ] Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
- [ ] Create a new cluster (free tier available)
- [ ] Create database user with read/write permissions
- [ ] Add `0.0.0.0/0` to IP whitelist (for Render access)
- [ ] Copy connection string (format: `mongodb+srv://...`)

#### Cloudinary (File Storage)
- [ ] Create account at [Cloudinary](https://cloudinary.com)
- [ ] Navigate to Dashboard
- [ ] Copy: Cloud Name, API Key, API Secret

#### API Keys
- [ ] Get Groq API key from [Groq](https://console.groq.com/)
- [ ] Get OpenAI API key from [OpenAI](https://platform.openai.com/)
- [ ] Get HuggingFace token from [HuggingFace](https://huggingface.co/settings/tokens)

#### JWT Secret
- [ ] Generate a random secure string (32+ characters)
  ```bash
  # On Mac/Linux:
  openssl rand -hex 32
  
  # On Windows PowerShell:
  -join ((65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
  ```

### 2. Code Preparation
- [ ] Push all changes to GitHub
- [ ] Verify `.gitignore` excludes `.env` files
- [ ] Test locally one more time
- [ ] Check that frontend `client.js` uses environment variable

---

## Render Deployment - Option 1 (Two Services)

### Backend Service

#### Create Service
- [ ] Go to [Render Dashboard](https://dashboard.render.com/)
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Configure:
  - [ ] **Name**: `docfusion-backend` (or your choice)
  - [ ] **Root Directory**: `backend`
  - [ ] **Runtime**: Python 3
  - [ ] **Build Command**: `pip install -r requirements.txt`
  - [ ] **Start Command**: `uvicorn api.server:app --host 0.0.0.0 --port $PORT`
  - [ ] **Instance Type**: Free (or upgrade for production)

#### Add Environment Variables
Go to service → Environment tab → Add the following:

- [ ] `MONGODB_URL` = `mongodb+srv://...` (from MongoDB Atlas)
- [ ] `JWT_SECRET_KEY` = `your-generated-secret`
- [ ] `GROQ_API_KEY` = `your-groq-key`
- [ ] `OPENAI_API_KEY` = `your-openai-key`
- [ ] `HUGGINGFACE_TOKEN` = `your-hf-token`
- [ ] `CLOUDINARY_CLOUD_NAME` = `your-cloud-name`
- [ ] `CLOUDINARY_API_KEY` = `your-cloudinary-key`
- [ ] `CLOUDINARY_API_SECRET` = `your-cloudinary-secret`

#### Deploy & Test
- [ ] Click "Create Web Service"
- [ ] Wait for deployment to complete (5-10 minutes first time)
- [ ] Copy backend URL: `https://______.onrender.com`
- [ ] Test health endpoint: `https://your-backend.onrender.com/api/health`
- [ ] Should return: `{"status": "ok"}`

### Frontend Service

#### Create Service
- [ ] Go to [Render Dashboard](https://dashboard.render.com/)
- [ ] Click "New +" → "Static Site"
- [ ] Connect same GitHub repository
- [ ] Configure:
  - [ ] **Name**: `docfusion-frontend` (or your choice)
  - [ ] **Root Directory**: `frontend`
  - [ ] **Build Command**: `npm install && npm run build`
  - [ ] **Publish Directory**: `dist`

#### Add Environment Variable
- [ ] `VITE_API_URL` = `https://your-backend-name.onrender.com` (from backend service)

#### Deploy
- [ ] Click "Create Static Site"
- [ ] Wait for deployment to complete (3-5 minutes)
- [ ] Copy frontend URL: `https://______.onrender.com`

### Update Backend CORS

#### Edit Code
- [ ] Open `backend/api/server.py` in your code editor
- [ ] Find `CORSMiddleware` configuration (around line 8-14)
- [ ] Update `allow_origins`:
  ```python
  allow_origins=[
      "https://your-frontend-name.onrender.com",  # ADD THIS
      "http://localhost:5173",  # Keep for local dev
  ]
  ```
- [ ] Save, commit, and push to GitHub:
  ```bash
  git add backend/api/server.py
  git commit -m "Update CORS for production"
  git push
  ```

#### Verify Deployment
- [ ] Render will auto-deploy backend with new changes
- [ ] Wait for backend to redeploy (2-3 minutes)

---

## Final Testing

### Backend Tests
- [ ] Visit: `https://your-backend.onrender.com/api/health`
- [ ] Should see: `{"status": "ok"}`
- [ ] Visit: `https://your-backend.onrender.com/docs`
- [ ] Should see: FastAPI Swagger documentation

### Frontend Tests
- [ ] Visit: `https://your-frontend.onrender.com`
- [ ] Should see: Login/Register page
- [ ] Open browser DevTools (F12) → Console
- [ ] No CORS errors should appear

### Full Application Test
- [ ] Create new account (Register)
- [ ] Login with credentials
- [ ] Create new session
- [ ] Upload a PDF document
- [ ] Wait for processing (first time may be slow due to model downloads)
- [ ] Ask a question about the document
- [ ] Verify response is relevant

---

## Troubleshooting

### Backend Issues

#### "Application failed to respond"
- [ ] Check Render logs for errors
- [ ] Verify all environment variables are set
- [ ] Check MongoDB connection string format
- [ ] Wait 60 seconds (cold start on free tier)

#### "MongoDB connection error"
- [ ] Verify MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- [ ] Check connection string format
- [ ] Verify database user has correct permissions
- [ ] Test connection string locally first

#### "Cloudinary error"
- [ ] Verify all three Cloudinary variables are set
- [ ] Check for typos in API keys
- [ ] Ensure account is active

### Frontend Issues

#### "CORS error" in browser console
- [ ] Verify backend CORS includes your frontend URL
- [ ] Check for `https://` vs `http://` mismatch
- [ ] Ensure backend is redeployed after CORS update
- [ ] Clear browser cache and try again

#### "API calls fail" or "Network error"
- [ ] Verify `VITE_API_URL` is set correctly in frontend
- [ ] Check browser DevTools → Network tab for failed requests
- [ ] Ensure backend URL ends without trailing slash
- [ ] Test backend health endpoint directly

#### Frontend shows blank page
- [ ] Check browser console for JavaScript errors
- [ ] Verify build completed successfully in Render logs
- [ ] Check that `dist` folder was published
- [ ] Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### General Issues

#### Changes not appearing
- [ ] Verify you pushed changes to GitHub
- [ ] Check Render deployment status
- [ ] Wait for deployment to complete
- [ ] Try clearing browser cache
- [ ] Check correct branch is being deployed

#### Slow performance
- [ ] First request after 15 min on free tier is slow (cold start)
- [ ] Model downloads on first document upload take time
- [ ] Consider upgrading to paid tier for production
- [ ] Check MongoDB Atlas is in same region as Render

---

## Post-Deployment

### Monitoring
- [ ] Bookmark your Render dashboard
- [ ] Set up Render notifications (optional)
- [ ] Monitor backend logs occasionally
- [ ] Check MongoDB Atlas usage

### Optional Improvements
- [ ] Set up custom domain
- [ ] Add monitoring/analytics
- [ ] Set up automated backups
- [ ] Configure auto-deploy on push
- [ ] Add staging environment

### Security
- [ ] Rotate JWT_SECRET_KEY periodically
- [ ] Monitor API key usage
- [ ] Review MongoDB access logs
- [ ] Keep dependencies updated

---

## Quick Reference

### Important URLs
- **Render Dashboard**: https://dashboard.render.com/
- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Cloudinary**: https://cloudinary.com/console
- **Backend API Docs**: `https://your-backend.onrender.com/docs`
- **Frontend**: `https://your-frontend.onrender.com`

### Useful Commands

```bash
# Generate JWT secret (Mac/Linux)
openssl rand -hex 32

# Check backend health
curl https://your-backend.onrender.com/api/health

# View Render logs (using Render CLI)
render logs -s your-service-name

# Test local before deploying
cd backend && uvicorn api.server:app --reload
cd frontend && npm run dev
```

### Support Resources
- [Render Docs](https://render.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vite Docs](https://vitejs.dev/)

---

## ✅ Deployment Complete!

If you've checked all items and tests pass, your application is live! 🎉

**Share your application:**
- Frontend URL: `https://your-frontend.onrender.com`

**For issues:**
- Check Render logs first
- Review this checklist
- See `DEPLOYMENT_GUIDE.md` for detailed troubleshooting

---

**Last Updated**: October 2025

