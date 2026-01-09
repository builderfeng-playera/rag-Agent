# Running Vercel Dev - Step by Step

## Command to Run

```bash
vercel dev --listen 3001
```

## Interactive Prompts You'll See

When you run the command, Vercel will ask you several questions:

### 1. "Set up and develop?"
   - **Answer:** `y` (yes)

### 2. "Link to existing project?"
   - If you've already deployed to Vercel: `y` (yes)
   - If this is first time: `n` (no)

### 3. "What's your project's name?"
   - **Answer:** `rag-agent` (or any name you prefer, lowercase)
   - Press Enter

### 4. "In which directory is your code located?"
   - **Answer:** `./` (or just press Enter for current directory)

### 5. "Want to override the settings?"
   - **Answer:** `n` (no)

## After Setup

Once setup is complete, you'll see:
```
> Ready! Available at http://localhost:3001
```

## Testing

Once the server is running, test it:

```bash
# Health check
curl http://localhost:3001/health

# Query endpoint
curl -X POST http://localhost:3001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FAISS?", "max_results": 3}'

# Chat endpoint  
curl -X POST http://localhost:3001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is FAISS?"}],
    "model": "supermind-agent-v1"
  }'
```

## Troubleshooting

### If it asks for login:
```bash
vercel login
```

### If port 3001 is busy:
```bash
vercel dev --listen 3002
```

### If you see errors about project name:
- Use a simple name: `rag-agent` (lowercase, no spaces)
- Avoid special characters

### To stop the server:
Press `Ctrl+C` in the terminal where it's running

## Alternative: Use Uvicorn (Faster for Local Dev)

If you just want to test locally without Vercel's serverless simulation:

```bash
uvicorn app:app --reload --port 8000
```

Then test at `http://localhost:8000`

