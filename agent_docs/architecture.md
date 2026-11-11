# Customer Support Automation System

## Technical Architecture

**Version:** 1.0\
**Architecture Style:** Simple modular RAG application\
**Primary UI:** Streamlit\
**Primary LLM:** Gemini\
**Vector Database:** ChromaDB

------------------------------------------------------------------------

## 1. Architecture Principle

The project should follow one important rule:

> Keep the implementation simple until complexity is actually required.

The first version should use understandable Python modules and
functions.

Do not introduce an agent framework, complex workflow engine,
microservices, message queues, or distributed infrastructure unless the
project actually needs them.

------------------------------------------------------------------------

## 2. High-Level Architecture

``` text
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    │                     │
                    │ Customer Chat       │
                    │ Admin Upload        │
                    │ Agent Tickets       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Application Layer   │
                    │                     │
                    │ Chat Service        │
                    │ Document Service    │
                    │ Ticket Service      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ RAG Service │   │ Ticket DB   │   │ LLM Service │
      └──────┬──────┘   └─────────────┘   └──────┬──────┘
             │                                    │
             ▼                                    ▼
      ┌─────────────┐                     ┌─────────────┐
      │ ChromaDB    │                     │ Gemini      │
      └─────────────┘                     └─────────────┘
```

------------------------------------------------------------------------

## 3. Document Ingestion Architecture

``` text
Admin Uploads Document
          │
          ▼
     File Validation
          │
          ▼
     Text Extraction
          │
          ▼
      Text Cleaning
          │
          ▼
        Chunking
          │
          ▼
 Metadata Generation
          │
          ▼
     Embedding Model
          │
          ▼
       ChromaDB
```

### Example chunk

``` text
Document:
Product Manual

Section:
Authentication

Page:
12

Content:
To reset your password, open Settings...
```

Metadata:

``` json
{
  "document_name": "product_manual.pdf",
  "document_type": "manual",
  "page": 12,
  "section": "authentication"
}
```

------------------------------------------------------------------------

## 4. Query Architecture

``` text
Customer Question
       │
       ▼
Query Embedding
       │
       ▼
ChromaDB Similarity Search
       │
       ▼
Top-K Chunks
       │
       ▼
Context Builder
       │
       ▼
Gemini
       │
       ▼
Answer
       │
       ▼
Source Citations
```

------------------------------------------------------------------------

## 5. Full Support Workflow

``` text
                         Customer
                            │
                            ▼
                         Question
                            │
                            ▼
                    ┌────────────────┐
                    │ Query Router   │
                    └───────┬────────┘
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
           RAG          Ticket Search    Human Request
             │              │               │
             ▼              ▼               │
        Retrieve         Existing            │
        Documents         Ticket             │
             │              │               │
             └───────┬──────┘               │
                     ▼                      │
                  Gemini                    │
                     │                      │
                     ▼                      │
               Answer Check                 │
                     │                      │
               ┌─────┴─────┐                │
               │           │                │
           Supported    Unsupported         │
               │           │                │
               ▼           └────────┬───────┘
            Answer                  ▼
               │               Create Ticket
               │                   │
               ▼                   ▼
            Customer          Support Agent
```

------------------------------------------------------------------------

## 6. Recommended Project Structure

Keep the structure small:

``` text
customer-support-ai/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   ├── documents/
│   └── chroma/
│
├── src/
│   ├── config.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── rag.py
│   ├── llm.py
│   ├── tickets.py
│   └── evaluation.py
│
├── pages/
│   ├── 1_Chat.py
│   ├── 2_Knowledge_Base.py
│   ├── 3_Tickets.py
│   └── 4_Evaluation.py
│
└── tests/
    └── test_rag.py
```

For a very small MVP, some modules can initially be combined. Split them
only when a file becomes difficult to understand.

------------------------------------------------------------------------

## 7. Module Responsibilities

### `document_loader.py`

Responsible for:

-   Reading PDF files
-   Reading TXT files
-   Reading DOCX files
-   Returning plain text

It should not generate embeddings.

### `chunker.py`

Responsible for:

-   Splitting text into chunks
-   Maintaining reasonable chunk size
-   Keeping useful metadata

### `embeddings.py`

Responsible for:

-   Loading the embedding model
-   Creating embeddings

### `vector_store.py`

Responsible for:

-   Creating/opening ChromaDB
-   Adding document chunks
-   Searching for relevant chunks
-   Removing documents

### `rag.py`

Responsible for:

-   Receiving the user query
-   Performing retrieval
-   Building context
-   Calling the LLM
-   Returning answer and sources

### `llm.py`

Responsible for:

-   Gemini configuration
-   Prompt creation
-   LLM calls

### `tickets.py`

Responsible for:

-   Creating tickets
-   Updating tickets
-   Reading tickets
-   Changing ticket status

### `evaluation.py`

Responsible for:

-   Running test questions
-   Comparing results
-   Producing evaluation metrics

------------------------------------------------------------------------

## 8. Simple RAG Logic

Conceptually:

``` python
def answer_question(question):
    chunks = search_documents(question)

    context = build_context(chunks)

    answer = generate_answer(
        question,
        context
    )

    return answer, chunks
```

This simple function should be the center of the MVP.

Do not create multiple layers of abstraction around it unless they solve
a real problem.

------------------------------------------------------------------------

## 9. Prompt Architecture

The LLM should receive:

``` text
SYSTEM INSTRUCTION

You are a customer support assistant.

Answer only using the supplied context.

If the context does not contain enough information,
say that you do not have enough information and
recommend escalation.

Do not invent policies, prices, procedures, or
product capabilities.

CONTEXT

[Retrieved chunks]

CUSTOMER QUESTION

[Question]
```

------------------------------------------------------------------------

## 10. Source Citation Architecture

Each retrieved chunk should retain metadata.

Example:

``` python
{
    "text": "...",
    "source": "product_manual.pdf",
    "page": 12,
    "section": "Authentication"
}
```

The final response can then show:

``` text
Answer:
You can reset your password from Settings > Security.

Sources:
- product_manual.pdf, page 12
- authentication_faq.pdf, page 4
```

------------------------------------------------------------------------

## 11. Escalation Architecture

Start with a simple rule-based mechanism.

Example:

``` text
Retrieved relevant chunks?
       │
   ┌───┴───┐
  YES      NO
   │        │
   ▼        ▼
Generate  Escalate
Answer    Ticket
```

Later, add:

``` text
Retrieval score
+
Answer validation
+
User request
+
Question category
```

Do not make the escalation system unnecessarily complex in the first
version.

------------------------------------------------------------------------

## 12. Data Flow

### Document Flow

``` text
File
 ↓
Loader
 ↓
Text
 ↓
Chunks
 ↓
Embeddings
 ↓
ChromaDB
```

### Customer Flow

``` text
Question
 ↓
Embedding
 ↓
ChromaDB
 ↓
Relevant Chunks
 ↓
Context
 ↓
Gemini
 ↓
Answer
 ↓
Sources
```

### Escalation Flow

``` text
Question
 ↓
Retrieval
 ↓
Insufficient Context
 ↓
Ticket
 ↓
Support Agent
```

------------------------------------------------------------------------

## 13. Database Design

For the first version, SQLite is sufficient for application data.

Tables:

``` text
documents
---------
id
name
type
uploaded_at
status

tickets
-------
id
customer_name
question
category
priority
status
created_at

messages
--------
id
ticket_id
role
content
created_at

feedback
--------
id
question
answer
rating
created_at
```

ChromaDB stores the document chunks and embeddings.

Later, SQLite can be replaced by PostgreSQL/Supabase.

------------------------------------------------------------------------

## 14. Technology Boundaries

Use:

``` text
Streamlit
    ↓
Python Services
    ↓
ChromaDB
    ↓
Gemini
```

Avoid initially:

``` text
Streamlit
 ↓
FastAPI
 ↓
Celery
 ↓
Redis
 ↓
Kafka
 ↓
Multiple microservices
```

The second architecture may be appropriate for a large production
system, but it is unnecessary for this portfolio MVP.

------------------------------------------------------------------------

## 15. Future Architecture

After the MVP is stable:

``` text
Streamlit
     │
     ▼
FastAPI
     │
     ▼
LangGraph
     │
 ┌───┼───────────────┐
 ▼   ▼               ▼
RAG Tickets      Escalation
 │
 ▼
Reranker
 │
 ▼
Vector DB
```

Only introduce these components after the simple version works.

------------------------------------------------------------------------

## 16. Architecture Decision Summary

  -----------------------------------------------------------------------
  Decision                Choice                  Reason
  ----------------------- ----------------------- -----------------------
  UI                      Streamlit               Simple and fast

  LLM                     Gemini                  Free-tier friendly

  Embeddings              Sentence Transformers   Easy local embedding

  Vector DB               ChromaDB                Simple local setup

  Database                SQLite initially        Minimal setup

  Orchestration           Python functions        Easy to understand

  Advanced orchestration  LangGraph later         Useful when workflow
                                                  grows

  API                     None initially          Streamlit can call
                                                  services directly

  Backend API             FastAPI later           Useful for production
                                                  separation
  -----------------------------------------------------------------------

The guiding principle is:

> Build the smallest working system first. Add complexity only when a
> requirement demands it.
