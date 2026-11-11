# Agent Instructions

## Customer Support Automation System

This file is the operating guide for an AI coding agent working on this
project.

------------------------------------------------------------------------

# 1. Your Role

You are the development agent responsible for implementing and
maintaining the Customer Support Automation System.

Your job is to:

-   Understand the existing project before changing it.
-   Implement features from the PRD.
-   Keep the code simple.
-   Keep modules easy to understand.
-   Avoid unnecessary abstractions.
-   Test changes before considering them complete.
-   Never invent project requirements.
-   Never add fake evaluation results.
-   Never claim a feature works if it has not been tested.

------------------------------------------------------------------------

# 2. Most Important Rule

## KEEP THE CODE SIMPLE

Prefer:

``` python
def search_documents(query):
    ...
```

over a complicated architecture with many classes when a function is
enough.

Prefer:

``` python
chunks = search_documents(question)
answer = generate_answer(question, chunks)
```

over multiple unnecessary services and abstractions.

The project is intended to be understandable by a developer reviewing
the repository.

------------------------------------------------------------------------

# 3. Read These Files First

Before making significant changes, read:

``` text
PRD.md
architecture.md
UI_design.md
agent_instruction.md
```

Then inspect the existing source code.

Do not assume the repository matches the documentation.

If the code and documentation disagree:

1.  Inspect the existing implementation.
2.  Identify the difference.
3.  Update the documentation if appropriate.
4.  Do not silently introduce a conflicting architecture.

------------------------------------------------------------------------

# 4. Development Principles

Follow these principles:

### Principle 1: Simplicity

Use the simplest implementation that satisfies the requirement.

### Principle 2: Readability

A beginner should be able to understand the main flow.

### Principle 3: Small modules

Each file should have one clear responsibility.

### Principle 4: No unnecessary frameworks

Do not introduce a framework just because it is popular.

### Principle 5: No fake functionality

Do not create buttons that pretend to work.

### Principle 6: No fake data

Do not invent customer tickets, accuracy results, evaluation scores, or
benchmark results.

### Principle 7: Test before completion

Run the relevant tests after implementing a feature.

------------------------------------------------------------------------

# 5. Core Technology Rules

Use:

``` text
Python
Streamlit
Gemini
Sentence Transformers
ChromaDB
SQLite
```

Optional later:

``` text
LangGraph
FastAPI
PostgreSQL/Supabase
Reranker
```

Do not add optional technologies unless they are actually required.

------------------------------------------------------------------------

# 6. Core RAG Flow

The main RAG flow is:

``` text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Top-K Chunks
   ↓
Context
   ↓
Gemini
   ↓
Answer
   ↓
Sources
```

Keep this flow visible in the code.

A developer should be able to trace the complete process without
navigating through many abstraction layers.

------------------------------------------------------------------------

# 7. Document Ingestion

When a document is uploaded:

``` text
Upload
 ↓
Validate
 ↓
Extract Text
 ↓
Clean Text
 ↓
Chunk Text
 ↓
Create Metadata
 ↓
Create Embeddings
 ↓
Store in ChromaDB
```

Do not skip metadata.

At minimum store:

``` text
document_name
document_type
page
section
```

when available.

------------------------------------------------------------------------

# 8. Chunking Rules

Start with a simple chunking strategy.

Example:

``` text
Chunk size: approximately 500-1000 words
Overlap: approximately 50-150 words
```

These are starting values, not fixed truths.

Evaluation should determine whether chunking needs adjustment.

Do not create an advanced semantic chunking system unless testing shows
that simple chunking is insufficient.

------------------------------------------------------------------------

# 9. Retrieval Rules

Start with:

``` text
similarity search
Top-K = 5
```

Make the value configurable.

Example:

``` python
TOP_K = 5
```

Do not scatter `5` throughout the code.

Later, if required:

``` text
Vector search
 ↓
Top 10-20
 ↓
Reranker
 ↓
Top 3-5
```

------------------------------------------------------------------------

# 10. LLM Rules

The LLM must receive the retrieved context.

Never allow the model to answer support questions without context when
the question requires company-specific information.

Use a simple grounding instruction:

``` text
Answer using only the supplied context.

If the context does not contain the answer,
say that you do not have enough information.

Do not invent information.
```

------------------------------------------------------------------------

# 11. Hallucination Prevention

If the retrieved documents do not support the answer:

``` text
Do not guess.
Do not invent.
Do not create a plausible answer.
```

Instead:

``` text
I couldn't find enough information in the available
support documentation to answer this reliably.
I've marked this for human support.
```

------------------------------------------------------------------------

# 12. Escalation

Use a simple escalation mechanism initially.

Escalate when:

-   The customer asks for human support.
-   Retrieval produces insufficient useful context.
-   The question requires an action the AI cannot perform.
-   The answer cannot be grounded in available documentation.
-   The issue is explicitly outside the supported scope.

Do not build a complicated confidence model before the basic RAG system
works.

------------------------------------------------------------------------

# 13. Ticket Workflow

Basic ticket states:

``` text
OPEN
 ↓
IN_REVIEW
 ↓
RESOLVED
```

Optional:

``` text
ESCALATED
CLOSED
```

Keep the state machine simple.

------------------------------------------------------------------------

# 14. Error Handling

Every external operation should have understandable error handling.

Examples:

``` text
Invalid document
Embedding failed
Vector database unavailable
Gemini API failed
Database error
```

The user should receive a clear message.

Do not expose API keys, stack traces, or internal secrets to users.

------------------------------------------------------------------------

# 15. Secrets

Never hardcode:

``` text
GEMINI_API_KEY
API keys
Passwords
Tokens
Database credentials
```

Use environment variables.

Example:

``` text
GEMINI_API_KEY=...
```

Use `.env` locally.

Never commit `.env`.

------------------------------------------------------------------------

# 16. Streamlit Rules

Keep the interface simple.

Use Streamlit components such as:

``` python
st.chat_message()
st.chat_input()
st.file_uploader()
st.button()
st.selectbox()
st.dataframe()
st.expander()
```

Avoid custom frontend frameworks.

------------------------------------------------------------------------

# 17. Project Structure

Prefer:

``` text
app.py

src/
    config.py
    document_loader.py
    chunker.py
    embeddings.py
    vector_store.py
    rag.py
    llm.py
    tickets.py
    evaluation.py

pages/
    1_Chat.py
    2_Knowledge_Base.py
    3_Tickets.py
    4_Evaluation.py
```

Do not create dozens of files for small functions.

------------------------------------------------------------------------

# 18. Implementation Order

Always implement in this order unless the user explicitly asks
otherwise.

## Step 1

Set up the Streamlit application.

## Step 2

Implement document loading.

## Step 3

Implement text chunking.

## Step 4

Implement embeddings.

## Step 5

Implement ChromaDB.

## Step 6

Implement document indexing.

## Step 7

Implement basic retrieval.

## Step 8

Implement Gemini response generation.

## Step 9

Display source citations.

## Step 10

Implement conversation history.

## Step 11

Implement ticket creation.

## Step 12

Implement human escalation.

## Step 13

Implement evaluation.

## Step 14

Improve retrieval only after evaluation identifies a problem.

------------------------------------------------------------------------

# 19. Testing Strategy

At minimum test:

### Document ingestion

``` text
PDF → text
TXT → text
DOCX → text
```

### Retrieval

``` text
Known question → relevant chunk
Unknown question → low/insufficient retrieval
```

### Generation

``` text
Context → grounded answer
No context → refusal/escalation
```

### Tickets

``` text
Create ticket
Update ticket
Resolve ticket
```

------------------------------------------------------------------------

# 20. Evaluation Rules

Never write:

``` text
Accuracy = 95%
```

unless the system actually produced that result using a defined
evaluation process.

The agent should create the evaluation framework, not fabricate the
result.

Store evaluation questions in something like:

``` text
evaluation/questions.json
```

Example:

``` json
[
  {
    "question": "How do I reset my password?",
    "expected_source": "authentication_faq.pdf"
  }
]
```

------------------------------------------------------------------------

# 21. Debugging Rules

When something fails:

1.  Read the error.
2.  Identify the actual failing component.
3.  Fix the smallest necessary part.
4.  Run the affected test.
5.  Check for regressions.

Do not rewrite the entire project to fix one error.

------------------------------------------------------------------------

# 22. Dependency Rules

Before adding a package:

Ask:

``` text
Do we actually need it?
```

If the answer is no, do not add it.

Prefer standard Python functionality when it is sufficient.

Keep `requirements.txt` small.

------------------------------------------------------------------------

# 23. Code Style

Prefer:

``` python
def create_ticket(question, category):
    ticket = {
        "question": question,
        "category": category,
        "status": "OPEN"
    }

    save_ticket(ticket)

    return ticket
```

Avoid unnecessary:

``` text
Factory
Manager
Registry
Provider
Adapter
Strategy
Repository
Service
Controller
```

classes unless they provide a real benefit.

------------------------------------------------------------------------

# 24. Comments

Comments should explain why something exists.

Good:

``` python
# Keep metadata so the UI can show the document page as a citation.
```

Avoid comments that simply repeat the code.

Bad:

``` python
# Create a list
chunks = []
```

------------------------------------------------------------------------

# 25. Before Editing Existing Code

Always inspect:

``` text
file structure
imports
configuration
database usage
existing functions
existing tests
```

Do not replace working code without understanding it.

------------------------------------------------------------------------

# 26. Before Creating a New Feature

Determine:

``` text
1. Which PRD requirement does it satisfy?
2. Which module should own it?
3. Can it be implemented with existing dependencies?
4. How will it be tested?
```

If there is no clear requirement, do not add the feature without user
approval.

------------------------------------------------------------------------

# 27. Definition of Done

A feature is complete only when:

``` text
Requirement implemented
        ↓
Code readable
        ↓
No unnecessary dependencies
        ↓
Error handling added
        ↓
Relevant test run
        ↓
Application starts
        ↓
Documentation updated if needed
```

------------------------------------------------------------------------

# 28. Final Rule

The most important instruction is:

> Build a simple RAG customer-support application that works reliably
> before trying to make it an advanced AI agent.

Do not optimize for architectural complexity.

Optimize for:

``` text
Correctness
+
Grounding
+
Simplicity
+
Readability
+
Testability
```
