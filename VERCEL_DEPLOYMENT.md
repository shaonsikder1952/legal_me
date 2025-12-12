# 🚀 Vercel Frontend Deployment Guide

## ⚠️ Critical Configuration

The error you're seeing happens because Vercel is looking in the wrong directory. Your repository has both `backend` and `frontend` folders, but Vercel needs to know to build only the `frontend`.

---

## 📋 Step-by-Step Deployment

### Step 1: Import Project to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `shaonsikder1952/legal_me`

### Step 2: Configure Build Settings

**CRITICAL**: Set the Root Directory to `frontend`

In the project configuration screen:

```
Framework Preset: Create React App
Root Directory: frontend    ← IMPORTANT!
Build Command: npm run build (or yarn build)
Output Directory: build
Install Command: npm install (or yarn install)
```

### Step 3: Environment Variables

Add this environment variable in Vercel:

```
REACT_APP_BACKEND_URL=https://your-railway-backend-url.railway.app
```

**Important**: 
- No trailing slash
- Must start with `REACT_APP_` (Create React App requirement)
- Replace with your actual Railway backend URL

### Step 4: Deploy

Click "Deploy" and Vercel will build your frontend.

---

## 🔧 If You Already Created the Project

If you already created the project and got the error, here's how to fix it:

1. Go to your Vercel project → **Settings**
2. Scroll to **Root Directory**
3. Click **Edit**
4. Set to: `frontend`
5. Click **Save**
6. Go to **Deployments** tab
7. Click the three dots (⋯) on the latest deployment
8. Click **Redeploy**

---

## 📁 Project Structure

Your monorepo structure:
```
legal_me/
├── backend/          ← Railway deploys this
│   ├── server.py
│   ├── requirements.txt
│   └── ...
└── frontend/         ← Vercel deploys this
    ├── package.json
    ├── src/
    ├── public/
    └── ...
```

Vercel needs to know to only build the `frontend` directory.

---

## ✅ Verification

After deployment, your frontend will be live at:
```
https://your-project.vercel.app
```

Test it:
1. Visit the URL
2. Should see the LegalMe home page
3. Try the chat and document analysis features

---

## 🐛 Common Issues & Fixes

### Issue 1: "Unexpected end of JSON input"
**Cause**: Vercel looking in wrong directory  
**Fix**: Set Root Directory to `frontend` in Vercel settings

### Issue 2: "Module not found" errors during build
**Cause**: Missing dependencies  
**Fix**: 
1. Ensure `package.json` has all dependencies
2. Delete `node_modules` and `package-lock.json`
3. Run `npm install` locally to regenerate
4. Commit and push changes
5. Redeploy on Vercel

### Issue 3: Backend API calls failing
**Cause**: Backend URL not configured or CORS issues  
**Fix**:
1. Set `REACT_APP_BACKEND_URL` in Vercel env variables
2. Ensure your Railway backend has CORS enabled (already configured)
3. Redeploy frontend

### Issue 4: Blank page after deployment
**Cause**: React Router not configured for SPA  
**Fix**: The `vercel.json` file handles this (already created)

---

## 🎯 Quick Checklist

Before deploying:
- [ ] Root Directory set to `frontend` in Vercel
- [ ] `REACT_APP_BACKEND_URL` environment variable added
- [ ] Backend is deployed and working on Railway
- [ ] `vercel.json` file exists in frontend folder

---

## 📝 Example Environment Variables

In Vercel dashboard → Your Project → Settings → Environment Variables:

```
REACT_APP_BACKEND_URL=https://legalme-backend.railway.app
```

**Note**: After adding/changing env vars, you must redeploy for changes to take effect.

---

## 🔗 Connecting Frontend to Backend

Once both are deployed:

1. **Backend on Railway**: `https://your-app.railway.app`
2. **Frontend on Vercel**: `https://your-project.vercel.app`

The frontend will make API calls to the backend URL you specified in `REACT_APP_BACKEND_URL`.

Make sure your backend's `CORS_ORIGINS` includes your Vercel URL:
```
CORS_ORIGINS=https://your-project.vercel.app
```

Or use `*` for all origins (less secure but easier for testing):
```
CORS_ORIGINS=*
```

---

## 🚀 Summary

1. ✅ Set **Root Directory** to `frontend` in Vercel
2. ✅ Add `REACT_APP_BACKEND_URL` environment variable
3. ✅ Deploy
4. ✅ Test your live application!

Your frontend will automatically redeploy when you push changes to GitHub.

---

## 📞 Still Having Issues?

If deployment fails after setting Root Directory:

1. **Check Build Logs**: Vercel Dashboard → Deployments → Click deployment → View logs
2. **Verify package.json**: Make sure all dependencies are listed
3. **Test Locally**: Run `cd frontend && npm install && npm run build` locally
4. **Clear Cache**: Vercel Settings → Clear build cache

---

## ✨ Files Created for Vercel

- ✅ `/app/frontend/vercel.json` - Vercel configuration (SPA routing)

This configuration ensures that all routes are handled by React Router (client-side routing).
