# Local Testing with Vercel Dev

## Running Vercel Dev Locally

### Option 1: Interactive Setup (Recommended)

Run in your terminal:
```bash
vercel dev
```

When prompted:
1. **Set up and develop?** → Yes
2. **Link to existing project?** → Yes (if you've deployed before) or No (to create new)
3. **Project name:** `rag-agent` (or your choice)
4. **Directory:** `./` (current directory)
5. **Override settings?** → No

The server will start on `http://localhost:3000`

### Option 2: Use Standard FastAPI Server (Faster for Development)

Instead of Vercel dev, you can test with uvicorn directly:

```bash
# Make sure you have the index files
ls my_notes.*

# Start the server
uvicorn app:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FAISS?", "max_results": 3}'
```

### Option 3: Test with Vercel Dev on Different Port

If port 3000 is busy:
```bash
vercel dev --listen 3001
```

## Troubleshooting

### "Project names can be up to 100 characters..."
- Use a simple name like `rag-agent` or `rag-agent-app`
- Avoid special characters except `.`, `_`, `-`

### Port Already in Use
- Kill the process using port 3000:
  ```bash
  lsof -ti:3000 | xargs kill -9
  ```
- Or use a different port: `vercel dev --listen 3001`

### Index Files Not Found
- Ensure `my_notes.index` and `my_notes_metadata.pkl` exist
- Run indexer if needed: `python indexer.py .`

### Environment Variables
- Vercel dev will use `.env` file automatically
- Or set: `export AI_BUILDER_TOKEN=your_token`

## Quick Test Commands

Once server is running:

```bash
# Health check
curl http://localhost:3000/health

# Query endpoint
curl -X POST http://localhost:3000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FAISS?", "max_results": 3}'

# Chat endpoint
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is FAISS?"}],
    "model": "supermind-agent-v1"
  }'
```

## Expected Output

### Health Check Response:
```json
{
  "status": "healthy",
  "index_loaded": true,
  "index_size": 25,
  "metadata_size": 25
}
```

### Query Response:
```json
{
  "query": "What is FAISS?",
  "results": [
    {
      "text": "...",
      "file_path": "...",
      "chunk_index": 0,
      "total_chunks": 8,
      "score": 0.85
    }
  ]
}
```

