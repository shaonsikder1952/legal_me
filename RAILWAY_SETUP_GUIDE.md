# 🚂 Railway Deployment - Complete Setup Guide

## ⚠️ CRITICAL: You Must Set Environment Variables

Your application is crashing because **required environment variables are missing**. Railway cannot start your app without these.

---

## 📋 Step-by-Step Deployment Instructions

### Step 1: Set Environment Variables in Railway

Go to your Railway project dashboard → **Variables** tab, and add these:

#### Required Variables:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=legalme
GROQ_API_KEY=your_groq_api_key_here
```

#### Optional Variables (with defaults):
```
CORS_ORIGINS=*
```

**Note**: Railway automatically provides `PORT` - you don't need to set it.

---

### Step 2: Get Your MongoDB URL

#### Option A: MongoDB Atlas (Recommended for Production)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Click "Connect" → "Connect your application"
4. Copy the connection string (looks like: `mongodb+srv://...`)
5. Replace `<password>` with your actual database password

#### Option B: Railway MongoDB Plugin
1. In Railway dashboard, click "New" → "Database" → "Add MongoDB"
2. Railway will automatically create a `MONGO_URL` variable
3. Use that URL for your backend

---

### Step 3: Get Your Groq API Key

To get your Groq API key:
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it as `GROQ_API_KEY` in Railway

**Model Used**: The app uses `llama-3.3-70b-versatile` (fast and high-quality)

---

### Step 4: Deploy to Railway

#### Method 1: Via Git (Recommended)
```bash
# Push your code to GitHub
git add .
git commit -m "Add Railway deployment configuration"
git push origin main

# Railway will auto-deploy when it detects changes
```

#### Method 2: Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

---

## 🔍 Verify Deployment

After deployment completes, test your API:

```bash
# Health check
curl https://your-app.railway.app/api/

# Expected response:
# {"message":"LegalMe API"}
```

---

## 🐛 Troubleshooting

### Error: "KeyError: 'MONGODB_URI'"
**Cause**: Environment variable not set  
**Fix**: Add `MONGODB_URI` in Railway Variables tab

### Error: "KeyError: 'GROQ_API_KEY'"
**Cause**: Environment variable not set  
**Fix**: Add `GROQ_API_KEY` in Railway Variables tab

### Error: "Could not find emergentintegrations"
**Cause**: Old build cache  
**Fix**: 
1. Railway Dashboard → Settings → "Clear Build Cache"
2. Redeploy

### OCR Not Working
**Cause**: Missing system packages  
**Fix**: The `nixpacks.toml` file is already included. If issues persist:
1. Check Railway build logs for tesseract installation
2. Ensure `nixpacks.toml` is in the `/backend` directory

### Application Timeout on Startup
**Cause**: MongoDB connection taking too long  
**Fix**:
1. Verify your `MONGO_URL` is correct
2. Check MongoDB Atlas network access (allow all IPs: `0.0.0.0/0`)
3. Increase Railway's timeout if needed

---

## 📁 Deployment Files (Already Created)

✅ `/app/backend/requirements.txt` - Python dependencies  
✅ `/app/backend/start.sh` - Startup script (installs emergentintegrations)  
✅ `/app/backend/Procfile` - Railway process file  
✅ `/app/backend/nixpacks.toml` - System package configuration  

---

## 🎯 Quick Checklist

Before deploying, ensure:
- [ ] `MONGODB_URI` is set in Railway
- [ ] `GROQ_API_KEY` is set in Railway
- [ ] `DB_NAME` is set (or use default "legalme")
- [ ] Code is pushed to GitHub
- [ ] Railway is connected to your GitHub repo

---

## 📞 Still Having Issues?

If you've set all environment variables and the app still won't start:

1. **Check Railway Logs**: 
   - Railway Dashboard → Deployments → Click latest deployment → View logs
   
2. **Verify Variables**:
   - Railway Dashboard → Variables → Ensure all keys are present
   
3. **Test MongoDB Connection**:
   ```bash
   # From your local machine
   mongosh "your_mongo_url_here"
   ```

4. **Clear Build Cache**:
   - Settings → Clear Build Cache → Redeploy

---

## ✨ Summary

Your app is **ready to deploy** once you:
1. ✅ Set `MONGODB_URI` in Railway Variables
2. ✅ Set `GROQ_API_KEY` in Railway Variables  
3. ✅ Set `DB_NAME=legalme` in Railway Variables (optional, defaults to "legalme")
4. ✅ Push code to GitHub
5. ✅ Railway will auto-deploy

**The crash you're seeing is normal** - the app cannot start without database credentials and API keys. This is a security feature! Once you add the variables, deployment will succeed. 🚀

## 🤖 LLM Configuration

The app now uses **Groq's Llama 3.3 70B** model (`llama-3.3-70b-versatile`):
- ⚡ Extremely fast inference
- 🎯 High quality responses
- 💰 Cost-effective
- 🔒 Your own API key (no shared credits)
