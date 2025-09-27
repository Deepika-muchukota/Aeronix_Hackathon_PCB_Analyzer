"""
RAG Vector Store using Chroma for persistent document storage and retrieval
"""
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

# Create storage directory
STORAGE_DIR = Path("out/chroma")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Chroma client
client = chromadb.PersistentClient(
    path=str(STORAGE_DIR),
    settings=Settings(anonymized_telemetry=False)
)

# Get or create collection
collection = client.get_or_create_collection(
    name="design_docs",
    metadata={"description": "Hardware design documents and specifications"}
)

def _hash(text: str) -> str:
    """Generate SHA1 hash for document ID"""
    return hashlib.sha1(text.encode('utf-8')).hexdigest()

def add_doc(name: str, text: str, meta: Optional[Dict[str, Any]] = None) -> str:
    """
    Add a document to the vector store
    
    Args:
        name: Document name (e.g., filename)
        text: Document content
        meta: Additional metadata
    
    Returns:
        Document ID
    """
    if not text.strip():
        return ""
    
    doc_id = _hash(text)
    metadata = {"name": name, "type": "design_doc"}
    if meta:
        metadata.update(meta)
    
    try:
        collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        return doc_id
    except Exception as e:
        print(f"Warning: Failed to add document {name}: {e}")
        return ""

def search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for relevant documents
    
    Args:
        query: Search query
        k: Number of results to return
    
    Returns:
        List of search results with id, text, and metadata
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(k, 10)  # Cap at 10 results
        )
        
        hits = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                hits.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "meta": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else 0.0
                })
        
        return hits
    except Exception as e:
        print(f"Warning: Search failed for query '{query}': {e}")
        return []

def get_doc_count() -> int:
    """Get total number of documents in the collection"""
    try:
        return collection.count()
    except Exception:
        return 0

def clear_library() -> bool:
    """Clear all documents from the library"""
    try:
        # Delete and recreate collection
        client.delete_collection("design_docs")
        global collection
        collection = client.get_or_create_collection(
            name="design_docs",
            metadata={"description": "Hardware design documents and specifications"}
        )
        return True
    except Exception as e:
        print(f"Warning: Failed to clear library: {e}")
        return False

def get_library_stats() -> Dict[str, Any]:
    """Get library statistics"""
    try:
        count = collection.count()
        return {
            "total_docs": count,
            "storage_path": str(STORAGE_DIR),
            "collection_name": "design_docs"
        }
    except Exception:
        return {
            "total_docs": 0,
            "storage_path": str(STORAGE_DIR),
            "collection_name": "design_docs"
        }

def search_context_for_entities(entities_text: str) -> str:
    """
    Search for relevant context based on entities found in the design
    
    Args:
        entities_text: Text containing detected entities
    
    Returns:
        Context blob for LLM enhancement
    """
    # Extract key terms for search
    search_terms = []
    
    # Look for voltage rails
    import re
    voltage_matches = re.findall(r'\+?[0-9]+\.?[0-9]*V', entities_text.upper())
    search_terms.extend(voltage_matches)
    
    # Look for components
    component_matches = re.findall(r'\b[A-Z]{2,}\d+[A-Z0-9\-]*\b', entities_text.upper())
    search_terms.extend(component_matches[:5])  # Limit to 5 components
    
    # Look for protocols
    protocol_matches = re.findall(r'\b(I2C|SPI|UART|CAN|USB)\b', entities_text.upper())
    search_terms.extend(protocol_matches)
    
    # Look for test commands
    test_matches = re.findall(r'\b(bit\.|test\.|check\.)\w+', entities_text.lower())
    search_terms.extend(test_matches)
    
    # Remove duplicates and search
    unique_terms = list(set(search_terms))[:10]  # Limit to 10 unique terms
    
    context_parts = []
    for term in unique_terms:
        hits = search(term, k=2)
        for hit in hits:
            # Truncate long texts
            text = hit["text"][:200] + "..." if len(hit["text"]) > 200 else hit["text"]
            context_parts.append(f"[{hit['meta']['name']}] {text}")
    
    return "\n".join(context_parts[:20])  # Limit to 20 context items
