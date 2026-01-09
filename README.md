# Markdown Notes RAG System

A local-first RAG (Retrieval-Augmented Generation) system for indexing and querying your Markdown notes using semantic search and agentic retrieval.

## Features

- **Local-First**: All data stays on your machine
- **Semantic Search**: Find relevant information using natural language queries
- **Agentic Retrieval**: AI agent autonomously searches your notes to answer questions
- **Simple & Fast**: Built with FAISS for efficient vector search
- **Web Interface**: FastAPI-based API for easy integration
- **Deployable**: Ready for GitHub and Vercel deployment

## Architecture

- **Indexer** (`indexer.py`): Recursively finds `.md` files, chunks them, generates embeddings, and builds a FAISS index
- **API Server** (`app.py`): FastAPI application with agentic retrieval tool that autonomously queries your notes

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
AI_BUILDER_TOKEN=your_token_here
```

The token is automatically injected if deploying via the AI Builder platform.

### 3. Index Your Notes

Run the indexer script on a folder containing your Markdown files:

```bash
python indexer.py /path/to/your/notes/folder
```

This will create:
- `my_notes.index`: FAISS vector index
- `my_notes_metadata.pkl`: Metadata mapping vectors to text chunks and file paths

**Options:**
- `--chunk-size`: Characters per chunk (default: 500)
- `--chunk-overlap`: Overlap between chunks (default: 50)

Example:
```bash
python indexer.py ~/Documents/notes --chunk-size 1000 --chunk-overlap 100
```

### 4. Start the API Server

```bash
uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Usage

### Direct Query Endpoint

Search your notes directly (non-agentic):

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did I learn about Python decorators?",
    "max_results": 5
  }'
```

### Agentic Chat Endpoint

Ask questions and let the agent search your notes autonomously:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the key insights from my notes about machine learning?"}
    ],
    "model": "supermind-agent-v1"
  }'
```

The agent will:
1. Detect that your question relates to your notes
2. Automatically search using `query_my_notes` tool
3. Refine searches if needed
4. Provide answers with source citations

### Web Interface

Open `index.html` in your browser or visit `http://localhost:8000` when the server is running.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions to:
- GitHub
- Vercel
- AI Builder Platform

## API Endpoints

### `GET /`
Root endpoint with API information and index status.

### `GET /health`
Health check endpoint showing index status.

### `POST /query`
Direct query endpoint (non-agentic).

**Request:**
```json
{
  "query": "your search query",
  "max_results": 5
}
```

**Response:**
```json
{
  "query": "your search query",
  "results": [
    {
      "text": "chunk text...",
      "file_path": "/path/to/file.md",
      "chunk_index": 0,
      "total_chunks": 5,
      "score": 0.85
    }
  ]
}
```

### `POST /chat`
Agentic chat endpoint with autonomous retrieval.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "your question"}
  ],
  "model": "supermind-agent-v1",
  "temperature": 0.7,
  "max_tokens": null
}
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "model": "supermind-agent-v1",
  "message": {
    "role": "assistant",
    "content": "Answer based on your notes..."
  },
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

## How It Works

1. **Indexing Phase**:
   - Recursively finds all `.md` files
   - Splits files into overlapping chunks
   - Generates embeddings using AI Builder API (`/v1/embeddings`)
   - Builds FAISS index for fast similarity search

2. **Query Phase**:
   - User asks a question via `/chat` endpoint
   - Agent analyzes the question
   - Agent autonomously calls `query_my_notes` tool with search queries
   - Tool generates query embedding and searches FAISS index
   - Agent receives results and synthesizes an answer
   - Agent can make multiple searches to gather comprehensive information

## Technical Details

- **Embedding Model**: `text-embedding-3-small` (via AI Builder API)
- **Vector Search**: FAISS with Inner Product (cosine similarity on normalized vectors)
- **Chunking**: Character-based with configurable size and overlap
- **Agent Model**: `supermind-agent-v1` (multi-tool agent with autonomous tool use)

## Evaluation & Testing

To evaluate the system according to your OKRs:

### Key Result 1: Hallucination Rate
Create a test set of 10 questions and verify that the AI doesn't invent facts not present in source documents. Target: <10% hallucination rate.

### Key Result 2: Retrieval Precision (Needle in a Haystack)
Create 3 test cases where a unique fact is buried in a large document:
1. Create a test document with a specific fact (the "needle")
2. Embed it in a much larger, irrelevant document (the "haystack")
3. Ask a question that can only be answered by finding that specific fact
4. Verify the system retrieves the correct chunk

Target: 100% pass rate on Needle in a Haystack tests.

## File Structure

```
.
├── indexer.py              # Indexing script
├── app.py                  # FastAPI application
├── api/
│   └── index.py           # Vercel serverless wrapper
├── index.html             # Web interface
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel configuration
├── README.md              # This file
├── DEPLOYMENT.md          # Deployment guide
├── RESEARCH_COMPARISON.md # Library comparison
├── .env                   # API key (not in git)
├── my_notes.index         # FAISS index (included for deployment)
└── my_notes_metadata.pkl  # Metadata (included for deployment)
```

## Troubleshooting

### Index not found
Run the indexer script first: `python indexer.py /path/to/notes`

### API key error
Ensure `AI_BUILDER_TOKEN` is set in your `.env` file or environment variables.

### No results returned
- Check that your index contains data: `GET /health`
- Try increasing `max_results` in your query
- Verify your search query is relevant to the indexed content

## License

MIT
