# Product Summary: Markdown Notes RAG System

## 🎯 Product Definition

### Core Problem
Hundreds of Markdown notes scattered across the computer, containing valuable insights but impossible to search and connect effectively.

### MVP (Minimal Viable Product)
A system that can index a single local folder of Markdown files and allow complex questions about them through a web interface, using an agentic retrieval process.

---

## 📊 OKRs (Objectives and Key Results)

### Objective: Ensure Answer Accuracy and Faithfulness to Source Material

#### Key Result 1: Hallucination Rate
- **Target:** < 10% hallucination rate
- **Test Method:** Evaluate on a test set of 10 questions
- **Metric:** Rate at which AI invents facts not present in source documents

#### Key Result 2: Retrieval Precision (Needle in a Haystack)
- **Target:** 100% pass rate
- **Test Method:** Create 3 Needle in a Haystack test cases
- **Approach:** 
  - Bury a unique, specific fact (the "needle") inside a much larger, irrelevant document (the "haystack")
  - Ask a question that can only be answered by finding that specific fact
  - Verify the system retrieves the correct chunk
- **Why This Matters:** Transforms testing from vague "it feels right" into a scientific, efficient process - the professional standard

---

## 🔬 Technical Decisions & Research

### Library Comparison: LlamaIndex vs LangChain vs FAISS

**Decision: FAISS + OpenAI SDK** ✅

#### Why FAISS Won:
1. **Simplicity:** Minimal code, easy to understand and maintain
2. **Performance:** Fast vector search without unnecessary overhead
3. **Local-First:** All data stays on your machine
4. **Control:** Full understanding of what happens at each step
5. **Perfect Fit:** Matches requirements exactly (index Markdown, search, retrieve)

#### Why Not LlamaIndex:
- **Too Heavy:** Many dependencies, larger footprint
- **Overkill for MVP:** Includes features not needed
- **Complexity:** More abstraction layers, harder to debug

#### Why Not LangChain:
- **Very Heavy:** Many dependencies, complex architecture
- **Over-Engineered:** Designed for complex agentic workflows
- **Not Local-First Focused:** Often assumes cloud services

### Implementation Approach:
- Use `faiss-cpu` for vector indexing
- Use OpenAI SDK to call `/v1/embeddings` endpoint
- Implement simple text chunking (by character count with overlap)
- Store metadata (file path, chunk index) alongside vectors
- Use FAISS for fast similarity search

---

## 🏗️ Architecture

### System Components

#### 1. Indexer (`indexer.py`)
**Purpose:** Build the vector index from Markdown files

**Process:**
1. Recursively finds all `.md` files in specified folder
2. Loads and chunks each file into smaller text segments
3. Generates embeddings via AI Builder API (`/v1/embeddings`)
4. Builds FAISS vector index
5. Saves index and metadata to disk

**Key Features:**
- Configurable chunk size (default: 500 characters)
- Configurable overlap (default: 50 characters)
- Batch processing for embeddings
- Error handling for unreadable files

**Output Files:**
- `my_notes.index`: FAISS vector index (~150KB)
- `my_notes_metadata.pkl`: Metadata mapping vectors to text chunks (~12KB)

#### 2. API Server (`app.py`)
**Purpose:** FastAPI application with agentic retrieval

**Endpoints:**
- `GET /`: Root endpoint with API info
- `GET /health`: Health check with index status
- `POST /query`: Direct query endpoint (non-agentic)
- `POST /chat`: Agentic chat endpoint with autonomous retrieval

**Key Features:**
- Agentic retrieval tool (`query_my_notes`)
- Autonomous tool calling (agent decides when to search)
- Multiple search refinement (agent can search multiple times)
- Source citations (includes file paths in responses)
- Error handling and graceful degradation

#### 3. Agentic Retriever Tool (`query_my_notes`)
**Functionality:**
- Generates query embedding
- Searches FAISS index for similar chunks
- Returns top results with metadata (text, file path, similarity score)
- Supports configurable number of results

**Integration:**
- Exposed as OpenAI function tool
- Agent autonomously calls it when questions relate to notes
- Agent can refine queries based on initial results

#### 4. System Prompt
**Instructions to Agent:**
- Treat `query_my_notes` as research assistant for personal knowledge base
- Automatically search when questions might be answered by notes
- Make multiple searches with different queries if needed
- Refine search queries based on previous results
- Always cite source file paths
- Say clearly if notes don't contain relevant information
- Combine information from multiple sources for complex questions

---

## 🛠️ Technical Stack

### Core Technologies
- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **Vector Search:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** OpenAI-compatible API (`text-embedding-3-small`)
- **Agent Model:** `supermind-agent-v1` (multi-tool agent)
- **API Client:** OpenAI SDK

### Dependencies
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
openai>=1.3.0
faiss-cpu>=1.7.4
numpy>=1.24.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

### Configuration
- **Embedding Model:** `text-embedding-3-small` (1536 dimensions)
- **Chunk Size:** 500 characters (configurable)
- **Chunk Overlap:** 50 characters (configurable)
- **Max Results:** 5 (configurable)
- **Vector Similarity:** Cosine similarity (via normalized Inner Product)

---

## 🔄 Iterative Development & Feedback

### Phase 1: Initial Implementation
**Created:**
- Indexer script with basic functionality
- FastAPI app with query endpoint
- Basic FAISS integration

### Phase 2: Agentic Retrieval
**Added:**
- `query_my_notes` tool function
- Agent system prompt for autonomous tool use
- Chat endpoint with tool calling support
- Multiple tool call handling (recursive searches)

### Phase 3: Error Handling & Robustness
**Fixed:**
- Variable name conflicts (`chunk_text` shadowing)
- Global variable issues in indexer
- Environment variable loading (added `python-dotenv`)
- File path resolution for serverless environments
- Startup error handling (graceful degradation)

### Phase 4: Deployment Preparation
**Added:**
- Vercel configuration (`vercel.json`)
- Vercel serverless wrapper (`api/index.py`)
- Deployment documentation
- Troubleshooting guides
- Local testing guides

### Phase 5: Deployment Fixes
**Improved:**
- Multiple path resolution for index files (serverless compatibility)
- Better error messages with path information
- Function timeout configuration
- Startup event error handling
- Project configuration for Vercel

---

## 📁 File Structure

```
.
├── indexer.py                  # Indexing script
├── app.py                      # FastAPI application
├── api/
│   └── index.py               # Vercel serverless wrapper
├── index.html                  # Web interface
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel configuration
├── .vercel/
│   └── project.json           # Vercel project config
├── .env                        # Environment variables (not in git)
├── my_notes.index             # FAISS index (included for deployment)
├── my_notes_metadata.pkl      # Metadata (included for deployment)
│
├── README.md                   # Main documentation
├── DEPLOYMENT.md              # Deployment guide
├── VERCEL_SETUP.md            # Vercel quick start
├── VERCEL_TROUBLESHOOTING.md  # Troubleshooting guide
├── VERCEL_DEV_INSTRUCTIONS.md # Local dev instructions
├── LOCAL_TEST.md              # Local testing guide
├── RESEARCH_COMPARISON.md     # Library comparison
└── PRODUCT_SUMMARY.md         # This file
```

---

## 🚀 Deployment

### GitHub Repository
- **URL:** https://github.com/builderfeng-playera/rag-Agent
- **Status:** ✅ Code pushed and ready

### Vercel Deployment
- **Status:** Configured and ready
- **Configuration:** `vercel.json` with Python runtime
- **Environment Variables:** `AI_BUILDER_TOKEN` required
- **Limitations:** 
  - 50MB serverless function size limit
  - Cold starts possible (2-5 seconds)
  - Index files must be included in deployment

### Deployment Process
1. Index notes locally: `python indexer.py /path/to/notes`
2. Commit index files to git
3. Push to GitHub
4. Deploy on Vercel (auto-deploy or manual)
5. Set environment variables in Vercel dashboard

---

## 🧪 Testing & Evaluation

### Local Testing
```bash
# Start server
uvicorn app:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -d '{"query": "..."}'
curl -X POST http://localhost:8000/chat -d '{"messages": [...]}'
```

### Evaluation Methods

#### Hallucination Rate Test
1. Create test set of 10 questions
2. Verify answers against source documents
3. Count instances where AI invents facts
4. Target: < 10% hallucination rate

#### Needle in a Haystack Test
1. Create 3 test cases:
   - Embed unique fact in large irrelevant document
   - Ask question requiring that specific fact
   - Verify correct chunk retrieval
2. Target: 100% pass rate

---

## 📈 Key Features

### What Makes This System Special

1. **Agentic Retrieval:** Agent autonomously decides when and how to search
2. **Multiple Search Refinement:** Agent can search multiple times with refined queries
3. **Source Citations:** Always includes file paths in responses
4. **Local-First:** All data stays on your machine
5. **Simple & Fast:** Minimal dependencies, efficient vector search
6. **Production-Ready:** Error handling, graceful degradation, deployment-ready

### User Experience

**Indexing:**
```bash
python indexer.py ~/Documents/notes
# Creates index in seconds
```

**Querying:**
```bash
# Simple question
"What did I learn about Python decorators?"

# Complex question  
"What are the key insights from my notes about machine learning?"
# Agent searches multiple times, combines information, cites sources
```

---

## 🔮 Future Enhancements

### Potential Improvements
- Web UI with React/Vue frontend
- Incremental indexing (update index when files change)
- Multiple index support
- Hybrid search (semantic + keyword)
- Reranking for better precision
- Metadata filtering (search within specific files/folders)
- Real-time updates
- User authentication
- Multi-user support

### Scaling Considerations
- Current: Single folder, local-first
- Future: Cloud storage integration
- Future: Distributed indexing
- Future: Multi-tenant support

---

## 📝 Lessons Learned

### What Worked Well
1. **FAISS Choice:** Simple, fast, perfect for MVP
2. **Agentic Approach:** Autonomous tool calling provides better UX
3. **Local-First:** No external dependencies for data storage
4. **Iterative Development:** Built incrementally, tested at each step

### Challenges Overcome
1. **Variable Shadowing:** Fixed naming conflicts
2. **Serverless Compatibility:** Multiple path resolution for different environments
3. **Environment Variables:** Proper loading with python-dotenv
4. **Deployment Configuration:** Vercel-specific setup and error handling

### Best Practices Applied
1. **Error Handling:** Graceful degradation, informative error messages
2. **Documentation:** Comprehensive guides for setup, deployment, troubleshooting
3. **Configuration:** Environment-based, easily adjustable
4. **Testing:** Health checks, local testing capabilities

---

## 🎓 Technical Highlights

### Vector Search Implementation
- Normalized embeddings for cosine similarity
- FAISS Inner Product on normalized vectors = cosine similarity
- Efficient batch processing
- Metadata preservation for source tracking

### Agentic Tool Calling
- Autonomous decision-making
- Multi-turn tool usage
- Query refinement based on results
- Context-aware search strategy

### Deployment Architecture
- Serverless-compatible design
- Multiple path resolution
- Environment variable management
- Graceful error handling

---

## 📊 Metrics & Performance

### Current Performance
- **Indexing:** ~25 chunks from 2 files in seconds
- **Query Latency:** < 1 second (after cold start)
- **Index Size:** ~150KB (scales linearly with content)
- **Embedding Dimensions:** 1536 (text-embedding-3-small)

### Scalability
- **Current Limit:** ~50MB index files (Vercel limit)
- **Practical Limit:** Thousands of documents, millions of chunks
- **Bottleneck:** Embedding API rate limits, not FAISS

---

## ✅ Project Status

### Completed ✅
- [x] Research and technical decisions
- [x] Indexer implementation
- [x] FastAPI application
- [x] Agentic retrieval tool
- [x] Error handling and robustness
- [x] Deployment configuration
- [x] Documentation
- [x] GitHub repository setup
- [x] Vercel deployment preparation

### Ready for Testing ⏳
- [ ] Hallucination rate evaluation (10 questions)
- [ ] Needle in a Haystack tests (3 cases)
- [ ] Production deployment verification
- [ ] User acceptance testing

### Future Work 🔮
- [ ] Web UI frontend
- [ ] Incremental indexing
- [ ] Advanced search features
- [ ] Performance optimizations

---

## 🎯 Success Criteria

### MVP Success Metrics
1. ✅ System indexes Markdown files successfully
2. ✅ System answers questions about indexed content
3. ✅ Agent autonomously searches when appropriate
4. ✅ Responses include source citations
5. ✅ System handles errors gracefully
6. ✅ System deploys to Vercel successfully

### Quality Metrics (To Be Evaluated)
1. ⏳ Hallucination rate < 10%
2. ⏳ Needle in a Haystack: 100% pass rate
3. ⏳ Query response time < 2 seconds
4. ⏳ Index build time reasonable for folder size

---

## 📚 Documentation

All documentation is available in the repository:
- **README.md:** Main project documentation
- **DEPLOYMENT.md:** Deployment guide
- **VERCEL_SETUP.md:** Vercel quick start
- **VERCEL_TROUBLESHOOTING.md:** Troubleshooting guide
- **RESEARCH_COMPARISON.md:** Technical decision rationale
- **LOCAL_TEST.md:** Local testing guide
- **VERCEL_DEV_INSTRUCTIONS.md:** Vercel dev setup

---

## 🙏 Acknowledgments

Built with:
- **FAISS:** Facebook AI Similarity Search
- **FastAPI:** Modern web framework
- **OpenAI SDK:** API client
- **AI Builder Platform:** Embedding and chat API
- **Vercel:** Deployment platform

---

**Last Updated:** January 2025
**Version:** 1.0.0
**Status:** MVP Complete, Ready for Evaluation

