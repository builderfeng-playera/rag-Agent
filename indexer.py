#!/usr/bin/env python3
"""
Indexer Script for Markdown Notes RAG System

This script recursively walks through a folder, finds all .md files,
chunks them, generates embeddings via the AI Builder API, and builds
a FAISS vector index for semantic search.
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # python-dotenv not installed, skip

from openai import OpenAI
import faiss
import numpy as np


# Configuration
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks
EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_FILE = "my_notes.index"
METADATA_FILE = "my_notes_metadata.pkl"


def get_openai_client() -> OpenAI:
    """Initialize OpenAI client with AI Builder API configuration."""
    api_key = os.getenv("AI_BUILDER_TOKEN")
    if not api_key:
        raise ValueError(
            "AI_BUILDER_TOKEN environment variable not set. "
            "Please set it in your .env file or environment."
        )
    
    return OpenAI(
        base_url="https://space.ai-builders.com/backend/v1",
        api_key=api_key
    )


def find_markdown_files(folder_path: str) -> List[Path]:
    """Recursively find all .md files in the specified folder."""
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    md_files = list(folder.rglob("*.md"))
    print(f"Found {len(md_files)} Markdown files")
    return md_files


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start position forward, accounting for overlap
        start = end - overlap
        
        # If we've reached the end, break
        if end >= len(text):
            break
    
    return chunks


def load_and_chunk_file(file_path: Path, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict[str, str]]:
    """
    Load a Markdown file and split it into chunks.
    
    Args:
        file_path: Path to the Markdown file
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of dictionaries with 'text' and 'metadata' keys
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []
    
    chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
    
    # Create metadata for each chunk
    chunk_metadata = []
    for i, chunk_content in enumerate(chunks):
        chunk_metadata.append({
            'text': chunk_content,
            'file_path': str(file_path),
            'chunk_index': i,
            'total_chunks': len(chunks)
        })
    
    return chunk_metadata


def generate_embeddings(client: OpenAI, texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts using the AI Builder API.
    
    Args:
        client: OpenAI client configured for AI Builder API
        texts: List of text strings to embed
    
    Returns:
        numpy array of embeddings (n_texts, embedding_dim)
    """
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Batch process embeddings (API supports multiple texts)
    all_embeddings = []
    
    # Process in batches to avoid overwhelming the API
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"  Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
        
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )
            
            # Extract embeddings from response
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            
        except Exception as e:
            print(f"Error generating embeddings for batch: {e}")
            raise
    
    # Convert to numpy array
    embeddings_array = np.array(all_embeddings, dtype=np.float32)
    
    print(f"Generated embeddings with shape: {embeddings_array.shape}")
    return embeddings_array


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS index from embeddings.
    
    Args:
        embeddings: numpy array of embeddings (n_vectors, embedding_dim)
    
    Returns:
        FAISS index object
    """
    dimension = embeddings.shape[1]
    
    # Use Inner Product (IP) index for cosine similarity
    # FAISS doesn't have a direct cosine similarity index, but we can normalize
    # embeddings and use Inner Product, which is equivalent to cosine similarity
    # for normalized vectors
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create index (using Inner Product for normalized vectors = cosine similarity)
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(embeddings)
    
    print(f"Built FAISS index with {index.ntotal} vectors")
    return index


def main():
    parser = argparse.ArgumentParser(
        description="Index Markdown files for semantic search"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder containing Markdown files"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Characters per chunk (default: {CHUNK_SIZE})"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Overlap between chunks (default: {CHUNK_OVERLAP})"
    )
    
    args = parser.parse_args()
    
    # Use parsed chunk settings
    chunk_size = args.chunk_size
    chunk_overlap = args.chunk_overlap
    
    print("=" * 60)
    print("Markdown Notes Indexer")
    print("=" * 60)
    
    # Step 1: Find all Markdown files
    print("\n[1/4] Finding Markdown files...")
    md_files = find_markdown_files(args.folder)
    
    if not md_files:
        print("No Markdown files found. Exiting.")
        return
    
    # Step 2: Load and chunk all files
    print("\n[2/4] Loading and chunking files...")
    all_chunks = []
    for md_file in md_files:
        chunks = load_and_chunk_file(md_file, chunk_size=chunk_size, overlap=chunk_overlap)
        all_chunks.extend(chunks)
        print(f"  Processed {md_file.name}: {len(chunks)} chunks")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    
    if not all_chunks:
        print("No chunks created. Exiting.")
        return
    
    # Step 3: Generate embeddings
    print("\n[3/4] Generating embeddings...")
    client = get_openai_client()
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = generate_embeddings(client, texts)
    
    # Step 4: Build FAISS index
    print("\n[4/4] Building FAISS index...")
    index = build_faiss_index(embeddings)
    
    # Step 5: Save index and metadata
    print("\n[Saving] Writing index and metadata to disk...")
    faiss.write_index(index, INDEX_FILE)
    
    # Save metadata (chunk texts and file paths)
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(all_chunks, f)
    
    print(f"\n✓ Index saved to: {INDEX_FILE}")
    print(f"✓ Metadata saved to: {METADATA_FILE}")
    print(f"\nIndex contains {index.ntotal} chunks from {len(md_files)} files")
    print("\nIndexing complete!")


if __name__ == "__main__":
    main()

