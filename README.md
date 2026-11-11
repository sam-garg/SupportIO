# SupportIO - AI Customer Support Automation Platform

An agentic, self-corrective, and grounded RAG (Retrieval-Augmented Generation) customer support platform built with **Streamlit**, **LangGraph**, **Pydantic**, **ChromaDB**, **Sentence-Transformers**, and **Dual LLM Orchestration (Google Gemini & Local Ollama / Llama 3.1)**.

---

## 🌟 Core Concepts & RAG Innovations

SupportIO implements modern production-grade RAG concepts to guarantee sub-second retrieval, hallucination prevention, adaptive query rewriting, and graceful escalation:

### 1. 🔄 Self-RAG & Corrective Adaptive Loops
- **Confidence & Relevance Thresholding:** Every retrieved chunk is scored against a minimum cosine similarity threshold (`SIMILARITY_THRESHOLD = 0.35`).
- **Self-Corrective Query Rewriting:** When low confidence or ambiguous matches are detected on the initial query, the pipeline does not guess or hallucinate. It triggers an intelligent query rewrite node to transform conversational customer phrasing into keyword-dense, documentation-optimized search queries and re-executes the search.
- **Circuit-Breaker & Escalation Fallback:** If retrieval remains insufficient after query reformulation, the pipeline activates an automated escalation path that crafts a courteous response and facilitates seamless ticket creation.

### 2. ⚡ Sub-Second Fast Vector Retrieval (HNSW + ChromaDB)
- **Local Embedding Ingestion:** Powered by Sentence-Transformers (`all-MiniLM-L6-v2`), generating dense 384-dimensional vector embeddings with zero external API latency.
- **HNSW Indexing with Cosine Metric:** ChromaDB uses Hierarchical Navigable Small World (HNSW) graphs configured for cosine similarity (`hnsw:space: cosine`), allowing fast approximate nearest neighbor (ANN) lookups across indexed chunks in milliseconds.
- **Sliding-Window Chunking with Overlap:** Text chunker splits documentation into windowed chunks (default `chunk_size=500` words, `chunk_overlap=50` words) while preserving document origin, page numbers, and structural context across boundaries.

### 3. 🛡️ Strict Grounding & Hallucination Defense
- **Zero-Unverified-Facts Constraint:** LLM system instructions explicitly prohibit speculative answers, pricing invention, or out-of-context claims.
- **Traceable Source Attribution:** Every response includes verifiable citation cards linking directly to the source document name, exact page number, and similarity score.
- **Negative Rejection Safeguards:** Recognizes missing or weak context and rejects speculative generation gracefully.

### 4. 🔀 Unified Dual LLM Architecture (Cloud & Edge / Local)
- **Cloud Mode:** High-speed inference using Google Gemini (`gemini-2.5-flash`).
- **Local / Edge Mode:** 100% offline, privacy-compliant inference with local Ollama (`llama3.1`, `mistral`, etc.).
- **Dynamic Hot-Swapping:** Switch between Cloud and Local inference directly from the web interface without restarting the service.

---

## 🏗️ LangGraph Agentic Pipeline Architecture

The RAG pipeline is orchestrated via **LangGraph** (`StateGraph`) with a strongly-typed **Pydantic** state schema (`RAGState`):

```text
                  [ User Question ]
                          │
                          ▼
                  [ retrieve_node ] ◄────────────────────────┐
                          │                                  │
                          ▼                                  │
               [ decide_after_retrieval ]                    │
                          │                                  │
         ┌────────────────┼────────────────┐                 │
         │ (High Match)   │ (Low - Retry 0)│ (Low - Retry 1) │
         ▼                ▼                ▼                 │
  [ generate_node ] [ rewrite_query ] [ escalate_node ]      │
         │                │                │                 │
         │                └────────────────┴─────────────────┘
         ▼                                 ▼
      [ END ]                           [ END ]
 (Grounded Answer)                  (Support Ticket)
```

### Node Lifecycle & State Flow:
1. **`retrieve_node`**: Vectorizes search query and queries ChromaDB HNSW index for Top-K semantic chunks.
2. **`decide_after_retrieval`**: Evaluates top match similarity against confidence thresholds:
   - `similarity >= 0.35` $\to$ Route to **`generate_node`**.
   - `similarity < 0.35` & `retry_count == 0` $\to$ Route to **`rewrite_query_node`**.
   - `similarity < 0.35` & `retry_count > 0` $\to$ Route to **`escalate_node`**.
3. **`rewrite_query_node`**: Uses the LLM to strip conversational noise and optimize technical keywords, updating `search_query` and looping back to `retrieve_node`.
4. **`generate_node`**: Formulates a grounded response with source citations.
5. **`escalate_node`**: Prepares an escalation payload and offers 1-click support ticket creation.

---

## 🚀 Quick Start

### 1. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Edit `.env` for your preferred LLM provider:
```ini
# Provider: 'gemini' (Cloud) or 'ollama' (Local Llama 3.1)
LLM_PROVIDER=gemini

# Google Gemini Settings (Cloud):
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Local Ollama Settings (e.g. Llama 3.1):
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Vector DB & Retrieval Settings:
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=4
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### 2. Run the Application
```bash
.venv\Scripts\streamlit run Home.py
```

### 3. Run Pipeline Verification Test
```bash
.venv\Scripts\python tests/test_rag.py
```

---

## 🧭 Application Modules & UI Pages

- **🎯 Home (`Home.py`):**
  - Live system overview (indexed documents, vector chunks, readiness status).
  - Quick navigation cards.
  - Active model selector (switch between Gemini and Ollama).

- **💬 Customer Chat (`pages/1_💬_Chat.py`):**
  - Grounded question answering strictly using retrieved document context.
  - Expandable source citations (Document name, page number, context snippet, similarity score).
  - Low-confidence automatic escalation button to create support tickets.
  - Helpful / Not Helpful feedback buttons logged to SQLite.

- **📚 Knowledge Base (`pages/2_📚_Knowledge_Base.py`):**
  - Upload PDF (PyMuPDF), DOCX (python-docx), TXT, and Markdown files.
  - Automatic sliding-window chunking with metadata preservation.
  - Real-time indexing into persistent ChromaDB vector store.
  - Document management table with 1-click deletion.

- **🎫 Support Tickets (`pages/3_🎫_Tickets.py`):**
  - Support agent dashboard to review escalated customer tickets.
  - Automated AI triage (Category classification, Priority, and Summary).
  - Inspect retrieved knowledge context and full conversation thread.
  - Draft response editor with status lifecycle (`OPEN` $\to$ `IN_REVIEW` $\to$ `RESOLVED` / `ESCALATED`).

- **📊 RAG Evaluation (`pages/4_📊_Evaluation.py`):**
  - Automated benchmark runner testing questions against ground-truth sources.
  - Real measured metrics: Retrieval Success Rate (%), Escalation Accuracy (%), and Response Latency (s).
  - Interactive UI form to add new evaluation test cases.

---

## 📁 Project Structure

```text
SupportIO/
├── Home.py                    # Main dashboard & navigation entrypoint
├── pages/
│   ├── 1_💬_Chat.py           # Customer chat with citations & escalation
│   ├── 2_📚_Knowledge_Base.py # Multi-format document uploader & indexing
│   ├── 3_🎫_Tickets.py        # Support agent triage & ticket resolver
│   └── 4_📊_Evaluation.py     # Real benchmark runner & accuracy metrics
├── src/
│   ├── config.py              # Central paths, models, and hyperparameters
│   ├── document_loader.py     # PDF (PyMuPDF), DOCX, TXT, and Markdown parsers
│   ├── chunker.py             # Sliding-window chunker with page metadata
│   ├── embeddings.py          # Sentence-Transformers local embedding model
│   ├── vector_store.py        # ChromaDB persistent store & similarity search
│   ├── tickets.py             # SQLite ticket queue, messaging, and feedback store
│   ├── llm.py                 # Unified Gemini & Ollama inference + triage
│   ├── rag.py                 # LangGraph + Pydantic Adaptive RAG pipeline
│   └── evaluation.py          # Benchmark evaluation harness
├── data/
│   ├── eval_questions.json    # Ground-truth evaluation dataset
│   └── documents/             # Uploaded support documents
├── tests/
│   └── test_rag.py            # End-to-end verification self-check
├── pyproject.toml             # Project dependencies and packaging configuration
├── .env.example               # Environment variables template
└── README.md                  # System documentation
```
