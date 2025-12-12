# Railway Deployment Checklist

## Current Status
✅ Code is ready for deployment
✅ All bugs fixed (section numbering, relevant laws display)
✅ Switched to Groq API (using llama-3.3-70b-versatile)
✅ Railway-specific files created:
  - `/app/backend/requirements.txt` (emergentintegrations removed)
  - `/app/backend/start.sh` (installs emergentintegrations + starts server)
  - `/app/backend/Procfile` (Railway startup command)
  - `/app/backend/.env.railway.template` (Environment variables template)

## The Problem You're Seeing
Railway is trying to build from the **old requirements.txt** that still contains `emergentintegrations==0.1.0`.

## Solution: Push Updated Code to Railway

### Option 1: If you're deploying from Git
1. **Commit the changes**:
   ```bash
   cd /app
   git add backend/requirements.txt backend/start.sh backend/Procfile backend/RAILWAY_DEPLOYMENT.md
   git commit -m "Fix Railway deployment: remove emergentintegrations from requirements.txt"
   git push origin main
   ```

2. **Trigger Railway rebuild**:
   - Go to your Railway dashboard
   - Click "Deploy" → "Trigger Deploy"
   - Or: Settings → "Clear Build Cache" → Redeploy

### Option 2: If deploying directly from Emergent
Since you're on Emergent platform, you need to:

1. **Save to GitHub** (use the Emergent UI feature)
   - Click "Save to Github" in the Emergent UI
   - This will push all current code to your connected repository

2. **Railway will auto-deploy**
   - Railway watches your GitHub repo
   - It will automatically detect the changes and start a new build

## What Railway Will Do (Correct Build Process)

1. **Install standard packages**: `pip install -r requirements.txt` ✅
2. **Run start.sh**:
   - Install emergentintegrations from custom index ✅
   - Start uvicorn server on port $PORT ✅

## Environment Variables to Set in Railway

Make sure these are set in your Railway project settings:

```
MONGO_URL=<your-mongodb-connection-string>
DB_NAME=legalme
EMERGENT_LLM_KEY=<your-emergent-llm-key>
CORS_ORIGINS=*
```

**Note**: Railway automatically provides the `PORT` variable - you don't need to set it.

## Verify Deployment

After Railway builds successfully, test:

```bash
# Health check
curl https://your-app.railway.app/api/

# Expected response:
# {"message":"LegalMe API"}
```

## If Build Still Fails

### Missing System Packages
If you get errors about tesseract or poppler, create `/app/backend/nixpacks.toml`:

```toml
[phases.setup]
aptPkgs = ['tesseract-ocr', 'poppler-utils']

[phases.install]
cmds = ['pip install -r requirements.txt']

[start]
cmd = 'bash start.sh'
```

Then commit and push again.

### Build Cache Issues
If Railway still uses old code:
1. Railway Dashboard → Settings → "Clear Build Cache"
2. Trigger a new deployment

## Summary

**Your code is deployment-ready!** The error you're seeing is because Railway hasn't pulled the updated code yet. Simply push to GitHub and Railway will rebuild with the correct configuration.

The fixed files are:
- ✅ `/app/backend/requirements.txt` - no emergentintegrations
- ✅ `/app/backend/start.sh` - installs emergentintegrations separately
- ✅ `/app/backend/Procfile` - correct startup command

**Next step**: Push to GitHub → Railway will auto-deploy → Test the API endpoint 🚀
