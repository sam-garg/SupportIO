import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.document_loader import load_document
from src.chunker import chunk_text
from src.vector_store import add_chunks, search_similarity, delete_document
from src.tickets import create_ticket, get_ticket, update_ticket_status

def test_full_pipeline():
    sample_doc = Path("data/documents/sample_support_guide.md")
    assert sample_doc.exists(), "Sample doc should exist"
    
    # 1. Document loading
    pages = load_document(sample_doc)
    assert len(pages) > 0, "Pages should be loaded"
    assert pages[0]["doc_type"] == "md"
    
    # 2. Chunking
    chunks = chunk_text(pages, chunk_size=100, chunk_overlap=10)
    assert len(chunks) > 0, "Chunks should be produced"
    
    # 3. Vector store indexing
    indexed_count = add_chunks(chunks)
    assert indexed_count == len(chunks), "All chunks should be indexed"
    
    # 4. Similarity retrieval
    hits = search_similarity("How do I reset my password?", top_k=2)
    assert len(hits) > 0, "Should retrieve relevant chunks"
    assert "password" in hits[0]["text"].lower()
    
    # 5. Tickets SQLite check
    tid = create_ticket("Need urgent help with billing", customer_name="Tester", category="Billing", priority="High")
    assert tid > 0
    t = get_ticket(tid)
    assert t["status"] == "OPEN"
    
    update_ticket_status(tid, "RESOLVED", "Issue fixed.")
    t_resolved = get_ticket(tid)
    assert t_resolved["status"] == "RESOLVED"
    assert len(t_resolved["messages"]) == 2
    
    print("[PASS] All pipeline checks passed successfully!")

if __name__ == "__main__":
    test_full_pipeline()
