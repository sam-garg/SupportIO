from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

from .vector_store import search_similarity
from .llm import generate_grounded_answer, call_llm
from .config import TOP_K

SIMILARITY_THRESHOLD = 0.35

class RAGState(BaseModel):
    question: str
    search_query: str = ""
    top_k: int = TOP_K
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    context: str = ""
    answer: str = ""
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    is_escalated: bool = False
    retry_count: int = 0

def format_context(chunks: List[Dict[str, Any]]) -> str:
    return "\n\n".join([
        f"--- SOURCE {i+1}: {c['metadata'].get('source', 'Doc')} (Page {c['metadata'].get('page', 1)}) ---\n{c['text']}"
        for i, c in enumerate(chunks)
    ])

def extract_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources, seen = [], set()
    for c in chunks:
        meta = c.get("metadata", {})
        key = (meta.get("source"), meta.get("page"))
        if key not in seen and meta.get("source"):
            seen.add(key)
            sources.append({
                "source": meta.get("source"),
                "page": meta.get("page", 1),
                "similarity": c.get("similarity", 0.0),
                "snippet": c.get("text", "")[:180] + "..." if len(c.get("text", "")) > 180 else c.get("text", "")
            })
    return sources

# --- LangGraph Nodes ---

def retrieve_node(state: RAGState) -> Dict[str, Any]:
    query = state.search_query if state.search_query else state.question
    chunks = search_similarity(query, top_k=state.top_k)
    return {
        "chunks": chunks,
        "context": format_context(chunks),
        "sources": extract_sources(chunks)
    }

def decide_after_retrieval(state: RAGState) -> str:
    chunks = state.chunks
    has_good_match = bool(chunks and max(c.get("similarity", 0.0) for c in chunks) >= SIMILARITY_THRESHOLD)
    
    if has_good_match:
        return "generate"
    elif state.retry_count == 0:
        return "rewrite_query"
    else:
        return "escalate"

def rewrite_query_node(state: RAGState) -> Dict[str, Any]:
    prompt = f"""You are a query optimization assistant for a support search engine.
Customer Question: {state.question}

Rewrite this question into a clear, concise keyword-rich search query to search technical documentation.
Output ONLY the rewritten search query with no quotes, explanations, or punctuation."""
    try:
        rewritten = call_llm(prompt).strip()
    except Exception:
        rewritten = state.question
    return {
        "search_query": rewritten if rewritten else state.question,
        "retry_count": state.retry_count + 1
    }

def generate_node(state: RAGState) -> Dict[str, Any]:
    answer = generate_grounded_answer(state.question, state.context)
    unsupported_markers = [
        "couldn't find enough information",
        "cannot find enough information",
        "do not have enough information",
        "not mentioned in the context",
        "not provided in the context"
    ]
    is_escalated = any(m in answer.lower() for m in unsupported_markers)
    return {
        "answer": answer,
        "is_escalated": is_escalated
    }

def escalate_node(state: RAGState) -> Dict[str, Any]:
    return {
        "answer": "I couldn't find enough information in the available support documentation to answer this reliably. Would you like to contact a support agent?",
        "is_escalated": True
    }

# --- Compile Workflow Graph ---

def create_rag_graph():
    graph = StateGraph(RAGState)
    
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("generate", generate_node)
    graph.add_node("escalate", escalate_node)

    graph.add_edge(START, "retrieve")
    
    graph.add_conditional_edges(
        "retrieve",
        decide_after_retrieval,
        {
            "generate": "generate",
            "rewrite_query": "rewrite_query",
            "escalate": "escalate"
        }
    )
    
    # Loop rewritten query back to retrieve
    graph.add_edge("rewrite_query", "retrieve")
    graph.add_edge("generate", END)
    graph.add_edge("escalate", END)

    return graph.compile()

_rag_graph = create_rag_graph()

def query_rag(question: str, top_k: int = TOP_K) -> Dict[str, Any]:
    """
    Executes the LangGraph Adaptive RAG pipeline with Pydantic state schema.
    """
    initial_state = RAGState(
        question=question,
        search_query=question,
        top_k=top_k
    )
    result = _rag_graph.invoke(initial_state)
    # result can be RAGState or dict depending on serialization
    if isinstance(result, dict):
        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "chunks": result.get("chunks", []),
            "is_escalated": result.get("is_escalated", False)
        }
    return {
        "answer": result.answer,
        "sources": result.sources,
        "chunks": result.chunks,
        "is_escalated": result.is_escalated
    }
