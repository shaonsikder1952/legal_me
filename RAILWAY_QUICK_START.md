# 🚀 Railway Deployment - Quick Start

## What You Need to Deploy

Your LegalMe app is ready for Railway! Just add these 2 environment variables:

### 📝 Step 1: Add to Railway Variables Tab

```
MONGODB_URI=your_mongodb_connection_string_here
GROQ_API_KEY=your_groq_api_key_here
```

Optional (has defaults):
```
DB_NAME=legalme
CORS_ORIGINS=*
```

---

## 🔑 Where to Get the Keys

### 1. MongoDB URI (`MONGODB_URI`)

**Option A: MongoDB Atlas (Recommended)**
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster (M0)
3. Click "Connect" → "Connect your application"
4. Copy connection string
5. Example: `mongodb+srv://user:pass@cluster.mongodb.net/`

**Option B: Railway MongoDB Plugin**
1. Railway Dashboard → "New" → "Database" → "MongoDB"
2. Railway auto-creates `MONGOURL` variable
3. Copy that value to `MONGODB_URI`

---

### 2. Groq API Key (`GROQ_API_KEY`)

1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up (free)
3. Create new API key
4. Copy the key (starts with `gsk_`)

**Model**: Uses Llama 3.3 70B (fast & high quality)

---

## 🎯 Deploy

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Railway auto-deploys** when it detects changes

3. **Test deployment**
   ```bash
   curl https://your-app.railway.app/api/
   # Should return: {"message":"LegalMe API"}
   ```

---

## ✅ That's It!

Your app will:
- ✅ Install all dependencies
- ✅ Install emergentintegrations 
- ✅ Start on Railway's dynamic PORT
- ✅ Connect to your MongoDB
- ✅ Use Groq for AI responses

---

## 🐛 Troubleshooting

### App crashes with "KeyError: 'MONGODB_URI'"
→ Add `MONGODB_URI` to Railway Variables

### App crashes with "KeyError: 'GROQ_API_KEY'"
→ Add `GROQ_API_KEY` to Railway Variables

### Build fails with "Could not find emergentintegrations"
→ Clear build cache in Railway settings and redeploy

### OCR not working
→ The `nixpacks.toml` file handles system dependencies automatically

---

## 📚 Detailed Guides

- Full setup: `/app/RAILWAY_SETUP_GUIDE.md`
- Deployment checklist: `/app/DEPLOYMENT_CHECKLIST.md`
- Backend deployment: `/app/backend/RAILWAY_DEPLOYMENT.md`
- Environment template: `/app/backend/.env.railway.template`

---

## 🎉 Summary

**Before**: Used Emergent LLM Key  
**Now**: Uses your own Groq API key

**Before**: Required `MONGO_URL`  
**Now**: Uses `MONGODB_URI` (Railway standard)

**Just add your 2 keys to Railway and deploy!** 🚀
