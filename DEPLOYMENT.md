# Deployment Guide

## GitHub Deployment

### Initial Setup

1. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit: RAG system for Markdown notes"
   git branch -M main
   git push -u origin main
   ```

2. **Note:** Index files (`my_notes.index` and `my_notes_metadata.pkl`) are included in the repository for deployment. For local development, you can regenerate them using the indexer script.

## Vercel Deployment

### Prerequisites

- Vercel account (sign up at https://vercel.com)
- GitHub repository connected to Vercel

### Steps

1. **Install Vercel CLI (optional but recommended):**
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Vercel Dashboard:**
   - Go to https://vercel.com/new
   - Import your GitHub repository: `builderfeng-playera/rag-Agent`
   - Vercel will auto-detect the Python project
   - Add environment variable: `AI_BUILDER_TOKEN` (get from your .env file)
   - Click "Deploy"

3. **Deploy via CLI:**
   ```bash
   vercel login
   vercel --prod
   ```
   When prompted:
   - Link to existing project or create new
   - Add environment variable `AI_BUILDER_TOKEN`

### Environment Variables

Set these in Vercel dashboard (Settings → Environment Variables):

- `AI_BUILDER_TOKEN`: Your AI Builder API token

### Important Notes for Vercel

⚠️ **Limitations:**
- Vercel serverless functions have a 50MB size limit
- FAISS index files must be under this limit
- Cold starts may occur (first request after inactivity)
- Index files are included in the deployment

### Alternative: AI Builder Platform Deployment

The AI Builder platform (mentioned in the API docs) might be better suited for this application:

1. Use the deployment API: `POST /v1/deployments`
2. See `app.py` for deployment endpoint details
3. The platform automatically injects `AI_BUILDER_TOKEN`

### Post-Deployment

1. **Verify deployment:**
   - Check health endpoint: `https://your-app.vercel.app/health`
   - Test query endpoint: `POST /query` or `/chat`

2. **Update frontend (if using index.html):**
   - Update API_URL in `index.html` to your Vercel URL
   - Or serve static files separately

3. **Re-index if needed:**
   - Run `python indexer.py /path/to/notes` locally
   - Commit and push updated index files
   - Redeploy on Vercel

## Troubleshooting

### Index files not found
- Ensure `my_notes.index` and `my_notes_metadata.pkl` are committed to git
- Check file sizes are under Vercel limits

### Environment variable issues
- Verify `AI_BUILDER_TOKEN` is set in Vercel dashboard
- Check it's available in production environment

### Import errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility (3.11+)

### FAISS installation issues
- Vercel should handle `faiss-cpu` automatically
- If issues occur, consider using `faiss` (GPU version) or alternative vector DB

