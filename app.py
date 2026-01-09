"""
FastAPI Application with Agentic RAG Retriever

This application provides a web interface for querying your indexed Markdown notes
using an agentic retrieval process. The agent autonomously uses the query_my_notes
tool to search your knowledge base.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # python-dotenv not installed, skip

import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from openai import OpenAI


# Configuration
INDEX_FILE = "my_notes.index"
METADATA_FILE = "my_notes_metadata.pkl"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_RESULTS = 5  # Number of top results to return


# Initialize FastAPI app
app = FastAPI(
    title="Markdown Notes RAG System",
    description="Agentic retrieval system for querying indexed Markdown notes",
    version="1.0.0"
)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global variables for index and metadata
faiss_index: Optional[faiss.Index] = None
metadata: List[Dict[str, Any]] = []
openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Initialize OpenAI client with AI Builder API configuration."""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("AI_BUILDER_TOKEN")
        if not api_key:
            raise ValueError(
                "AI_BUILDER_TOKEN environment variable not set. "
                "Please set it in your .env file or environment."
            )
        
        openai_client = OpenAI(
            base_url="https://space.ai-builders.com/backend/v1",
            api_key=api_key
        )
    return openai_client


def load_index():
    """Load the FAISS index and metadata from disk."""
    global faiss_index, metadata
    
    # Try multiple possible paths for serverless environments
    possible_index_paths = [
        INDEX_FILE,  # Current directory
        Path(__file__).parent / INDEX_FILE,  # App directory
        Path.cwd() / INDEX_FILE,  # Working directory
    ]
    
    possible_metadata_paths = [
        METADATA_FILE,
        Path(__file__).parent / METADATA_FILE,
        Path.cwd() / METADATA_FILE,
    ]
    
    index_path = None
    metadata_path = None
    
    for path in possible_index_paths:
        if Path(path).exists():
            index_path = path
            break
    
    for path in possible_metadata_paths:
        if Path(path).exists():
            metadata_path = path
            break
    
    if not index_path:
        error_msg = (
            f"Index file '{INDEX_FILE}' not found. "
            f"Searched in: {[str(p) for p in possible_index_paths]}. "
            f"Current directory: {Path.cwd()}. "
            f"Please ensure index files are included in deployment."
        )
        print(f"ERROR: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    if not metadata_path:
        error_msg = (
            f"Metadata file '{METADATA_FILE}' not found. "
            f"Searched in: {[str(p) for p in possible_metadata_paths]}. "
            f"Please ensure metadata files are included in deployment."
        )
        print(f"ERROR: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    try:
        # Load FAISS index
        faiss_index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        print(f"✓ Loaded index from {index_path}")
        print(f"✓ Loaded metadata from {metadata_path}")
        print(f"✓ Index contains {faiss_index.ntotal} vectors and {len(metadata)} metadata entries")
    except Exception as e:
        print(f"ERROR loading index: {e}")
        raise


# Load index on startup
@app.on_event("startup")
async def startup_event():
    """Load the index when the application starts."""
    try:
        load_index()
        print("✓ Index loaded successfully")
    except FileNotFoundError as e:
        print(f"⚠ Warning: {e}")
        print("  The application will start, but queries will fail until the index is created.")
    except Exception as e:
        print(f"⚠ Error loading index: {e}")
        print("  The application will start, but queries will fail.")


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = MAX_RESULTS


class SearchResult(BaseModel):
    text: str
    file_path: str
    chunk_index: int
    total_chunks: int
    score: float


class QueryResponse(BaseModel):
    results: List[SearchResult]
    query: str


# Tool function for querying notes
def query_my_notes(query: str, max_results: int = MAX_RESULTS) -> List[Dict[str, Any]]:
    """
    Search the indexed Markdown notes using semantic similarity.
    
    This function:
    1. Generates an embedding for the query
    2. Searches the FAISS index for similar chunks
    3. Returns the top results with their metadata
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of dictionaries containing:
        - text: The chunk text
        - file_path: Path to the source file
        - chunk_index: Index of the chunk in the file
        - total_chunks: Total chunks in the source file
        - score: Similarity score (higher is more similar)
    """
    global faiss_index, metadata
    
    if faiss_index is None or len(metadata) == 0:
        raise ValueError(
            "Index not loaded. Please ensure the indexer has been run "
            "and the index files exist."
        )
    
    # Generate embedding for the query
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query]
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
    
    # Normalize for cosine similarity (same as index)
    faiss.normalize_L2(query_embedding)
    
    # Search the index
    k = min(max_results, faiss_index.ntotal)
    scores, indices = faiss_index.search(query_embedding, k)
    
    # Retrieve results with metadata
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:  # FAISS returns -1 for invalid indices
            continue
        
        chunk_meta = metadata[idx]
        results.append({
            'text': chunk_meta['text'],
            'file_path': chunk_meta['file_path'],
            'chunk_index': chunk_meta['chunk_index'],
            'total_chunks': chunk_meta['total_chunks'],
            'score': float(score)
        })
    
    return results


# API endpoint for direct querying (non-agentic)
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Direct query endpoint for searching notes.
    
    This is a simple endpoint that returns search results directly.
    For agentic retrieval, use the /chat endpoint instead.
    """
    try:
        results = query_my_notes(request.query, request.max_results or MAX_RESULTS)
        return QueryResponse(
            query=request.query,
            results=[SearchResult(**r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat completion endpoint with agentic retrieval
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "supermind-agent-v1"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint with agentic retrieval.
    
    The agent will autonomously use the query_my_notes tool when it detects
    that a question might be answered by your notes.
    """
    client = get_openai_client()
    
    # Define the query_my_notes tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_my_notes",
                "description": (
                    "Search your personal knowledge base of indexed Markdown notes. "
                    "Use this tool when the user asks questions that might be answered "
                    "by your notes. You can call this tool multiple times with different "
                    "queries to gather comprehensive information. The tool returns the "
                    "most relevant text chunks along with their source file paths and "
                    "similarity scores."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "The search query. Formulate this as a question or "
                                "keyword search that would help find relevant information "
                                "in the notes. Be specific and targeted."
                            )
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    # System prompt instructing the agent to use the tool
    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant with access to a personal knowledge base "
            "of Markdown notes. When users ask questions that might be answered by "
            "their notes, you should autonomously use the query_my_notes tool to search "
            "for relevant information.\n\n"
            "Guidelines for using query_my_notes:\n"
            "1. When a question relates to information that might be in the notes, "
            "automatically search without asking\n"
            "2. You can make multiple searches with different queries to gather "
            "comprehensive information\n"
            "3. If initial results aren't sufficient, refine your search queries "
            "based on what you learned\n"
            "4. Always cite the source file paths when referencing information from notes\n"
            "5. If the notes don't contain relevant information, say so clearly\n"
            "6. Combine information from multiple sources when answering complex questions\n\n"
            "Your goal is to be a research assistant that proactively searches the "
            "knowledge base to provide accurate, well-sourced answers."
        )
    }
    
    # Prepare messages with system prompt
    messages = [system_prompt] + [msg.dict() for msg in request.messages]
    
    # Make the chat completion request with tool calling support
    try:
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            response = client.chat.completions.create(
                model=request.model or "supermind-agent-v1",
                messages=messages,
                tools=tools,
                tool_choice="auto",  # Let the agent decide when to use tools
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens
            )
            
            message = response.choices[0].message
            
            # If the agent called a tool, execute it and continue
            if message.tool_calls:
                # Add assistant message with tool calls to conversation
                assistant_msg = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                }
                messages.append(assistant_msg)
                
                # Execute all tool calls
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "query_my_notes":
                        import json
                        try:
                            args = json.loads(tool_call.function.arguments)
                            query = args.get("query", "")
                            max_results = args.get("max_results", MAX_RESULTS)
                            
                            # Execute the tool
                            results = query_my_notes(query, max_results)
                            
                            # Format results for the agent
                            results_text = f"Search results for query: '{query}'\n\n"
                            if results:
                                for i, result in enumerate(results, 1):
                                    results_text += (
                                        f"Result {i} (similarity: {result['score']:.4f}):\n"
                                        f"Source: {result['file_path']}\n"
                                        f"Chunk {result['chunk_index'] + 1}/{result['total_chunks']}\n"
                                        f"Content: {result['text']}\n\n"
                                    )
                            else:
                                results_text = f"No results found for query: '{query}'"
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": results_text
                            })
                        except Exception as e:
                            # Add error message if tool execution fails
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Error executing query_my_notes: {str(e)}"
                            })
                    else:
                        # Unknown tool call
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Unknown tool: {tool_call.function.name}"
                        })
                
                iteration += 1
                continue  # Continue the loop to get the agent's response
            
            # No tool calls, return the final response
            return {
                "id": response.id,
                "model": response.model,
                "message": {
                    "role": message.role,
                    "content": message.content
                },
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        # If we hit max iterations, return the last response
        return {
            "id": response.id,
            "model": response.model,
            "message": {
                "role": message.role,
                "content": message.content or "Maximum iterations reached. Please try a simpler query."
            },
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "index_loaded": faiss_index is not None,
        "index_size": faiss_index.ntotal if faiss_index else 0,
        "metadata_size": len(metadata)
    }


@app.get("/")
async def root():
    """Serve the web interface or return API information."""
    # Check if index.html exists, serve it if available
    if Path("index.html").exists():
        return FileResponse("index.html")
    
    # Otherwise return API information
    return {
        "name": "Markdown Notes RAG System",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST - Direct query endpoint (non-agentic)",
            "/chat": "POST - Chat endpoint with agentic retrieval",
            "/health": "GET - Health check"
        },
        "index_status": {
            "loaded": faiss_index is not None,
            "size": faiss_index.ntotal if faiss_index else 0
        }
    }

