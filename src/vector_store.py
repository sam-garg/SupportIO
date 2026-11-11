from typing import List, Dict, Any
import chromadb
from .config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from .embeddings import embed_texts, embed_query

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _chroma_client

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks(chunks: List[Dict[str, Any]]) -> int:
    if not chunks:
        return 0
    collection = get_collection()
    
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    embeddings = embed_texts(texts)
    
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )
    return len(chunks)

def search_similarity(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    
    query_emb = embed_query(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )
    
    hits = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for doc, meta, dist in zip(docs, metas, distances):
            # cosine similarity is approx 1 - cosine distance
            hits.append({
                "text": doc,
                "metadata": meta,
                "distance": dist,
                "similarity": round(1.0 - dist, 4)
            })
    return hits

def delete_document(doc_name: str) -> None:
    collection = get_collection()
    collection.delete(where={"source": doc_name})

def get_indexed_documents() -> List[str]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    all_data = collection.get(include=["metadatas"])
    sources = set()
    for meta in all_data.get("metadatas", []):
        if meta and "source" in meta:
            sources.add(meta["source"])
    return sorted(list(sources))

def get_stats() -> Dict[str, Any]:
    collection = get_collection()
    count = collection.count()
    docs = get_indexed_documents()
    return {
        "chunk_count": count,
        "document_count": len(docs),
        "documents": docs
    }
