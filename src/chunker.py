from typing import List, Dict, Any

def chunk_text(
    pages: List[Dict[str, Any]], 
    chunk_size: int = 500, 
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Chunks text by words with sliding overlap while preserving metadata.
    """
    chunks = []
    chunk_idx = 0

    for page_item in pages:
        words = page_item["text"].split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text_str = " ".join(chunk_words)

            chunks.append({
                "chunk_id": f"{page_item['source']}_p{page_item['page']}_c{chunk_idx}",
                "text": chunk_text_str,
                "metadata": {
                    "source": page_item["source"],
                    "page": page_item["page"],
                    "doc_type": page_item.get("doc_type", "unknown")
                }
            })
            chunk_idx += 1
            if end >= len(words):
                break
            start += chunk_size - chunk_overlap

    return chunks
