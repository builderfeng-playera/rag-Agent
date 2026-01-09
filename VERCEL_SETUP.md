# Vercel Deployment Quick Start

## ✅ Code is now on GitHub!

Repository: https://github.com/builderfeng-playera/rag-Agent

## Deploy to Vercel

### Option 1: Via Vercel Dashboard (Recommended)

1. **Go to Vercel:**
   - Visit https://vercel.com/new
   - Sign in with GitHub

2. **Import Repository:**
   - Click "Import Git Repository"
   - Select `builderfeng-playera/rag-Agent`
   - Click "Import"

3. **Configure Project:**
   - **Framework Preset:** Other (or leave auto-detected)
   - **Root Directory:** `./` (default)
   - **Build Command:** Leave empty (Vercel auto-detects Python)
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements.txt`

4. **Add Environment Variable:**
   - Go to "Environment Variables"
   - Add: `AI_BUILDER_TOKEN` = `sk_e5ec71d9_a491add896e4e94da35be769927505a579f8`
   - Select all environments (Production, Preview, Development)

5. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)

### Option 2: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# When prompted:
# - Link to existing project? No (create new)
# - Project name: rag-agent (or your choice)
# - Directory: ./
# - Override settings? No
```

Then add environment variable:
```bash
vercel env add AI_BUILDER_TOKEN
# Paste: sk_e5ec71d9_a491add896e4e94da35be769927505a579f8
# Select: Production, Preview, Development
```

## ⚠️ Important Notes

### Vercel Limitations

1. **Serverless Function Size Limit:** 50MB
   - Your index files (~150KB) are well under this limit ✅
   - FAISS library adds ~10-20MB, still within limits ✅

2. **Cold Starts:**
   - First request after inactivity may take 2-5 seconds
   - Subsequent requests are fast

3. **File System:**
   - Index files are included in deployment
   - They're read-only at runtime
   - To update index: regenerate locally, commit, and redeploy

### Testing Deployment

After deployment, test your endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# Query endpoint
curl -X POST https://your-app.vercel.app/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FAISS?", "max_results": 3}'

# Chat endpoint
curl -X POST https://your-app.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is FAISS?"}],
    "model": "supermind-agent-v1"
  }'
```

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify Python version (3.11+)
- Check build logs in Vercel dashboard

### Runtime Errors
- Verify `AI_BUILDER_TOKEN` is set correctly
- Check function logs in Vercel dashboard
- Ensure index files are committed to git

### Import Errors
- Verify `api/index.py` exists and imports correctly
- Check that `app.py` is in the root directory

## Alternative: AI Builder Platform

If Vercel has issues, consider using the AI Builder deployment platform:

1. The API supports deployment via `POST /v1/deployments`
2. See `DEPLOYMENT.md` for details
3. Automatically handles environment variables

## Next Steps

1. ✅ Code pushed to GitHub
2. ⏳ Deploy to Vercel (follow steps above)
3. ⏳ Test endpoints
4. ⏳ Update `index.html` with your Vercel URL
5. ⏳ Share your deployed app!

