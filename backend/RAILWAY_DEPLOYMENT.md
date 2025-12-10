# Railway Deployment Guide for LegalMe

This document explains how to deploy the LegalMe application on Railway.

## Prerequisites
- Railway account
- This GitHub repository connected to Railway

## Configuration

### 1. Environment Variables
Set the following environment variables in your Railway project:

```
MONGO_URL=<your-mongodb-connection-string>
DB_NAME=legalme
EMERGENT_LLM_KEY=<your-emergent-llm-key>
CORS_ORIGINS=*
PORT=8001
```

### 2. Key Files

#### `/backend/requirements.txt`
Contains all Python dependencies EXCEPT `emergentintegrations` (which requires a custom index URL).

#### `/backend/start.sh`
This startup script:
1. Installs `emergentintegrations` from the custom package index
2. Starts the FastAPI server with uvicorn, binding to `0.0.0.0` and the Railway-provided PORT

```bash
#!/bin/bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
PORT=${PORT:-8001}
uvicorn server:app --host 0.0.0.0 --port $PORT
```

#### `/backend/Procfile`
Railway process file that runs the startup script:
```
web: bash start.sh
```

### 3. System Dependencies

LegalMe uses OCR and PDF processing, which require system-level packages:
- `tesseract-ocr` (for OCR on images and scanned PDFs)
- `poppler-utils` (for PDF to image conversion)

If Railway's default buildpack doesn't include these, you may need to create a `nixpacks.toml` file:

```toml
[phases.setup]
aptPkgs = ['tesseract-ocr', 'poppler-utils']

[phases.install]
cmds = ['pip install -r requirements.txt']

[start]
cmd = 'bash start.sh'
```

## Deployment Steps

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Set Environment Variables**: Add all required env vars in Railway dashboard
3. **Deploy**: Railway will automatically detect the Procfile and deploy

## Troubleshooting

### Build Failures
- Check Railway logs for specific error messages
- Verify all environment variables are set correctly
- Ensure system dependencies are installed (add nixpacks.toml if needed)

### Application Errors
- Check application logs in Railway dashboard
- Verify MongoDB connection string is correct
- Test the API endpoint: `https://your-app.railway.app/api/`

### OCR Issues
If OCR isn't working, tesseract-ocr may not be installed:
1. Add a nixpacks.toml file (as shown above)
2. Redeploy the application

## Health Check
Test if the API is running:
```bash
curl https://your-app.railway.app/api/
```

Expected response:
```json
{"message":"LegalMe API"}
```

## Important Notes
- The `PORT` environment variable is automatically provided by Railway
- Do NOT hardcode port 8001 in your code - always use `os.environ.get('PORT', 8001)`
- The `start.sh` script MUST be executable: `chmod +x start.sh`
- `emergentintegrations` cannot be in requirements.txt - it must be installed separately via the custom index
