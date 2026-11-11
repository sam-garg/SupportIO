# Customer Support Automation System

## Streamlit UI Design Specification

**Version:** 1.0\
**Design Goal:** Simple, clean, easy to understand\
**Framework:** Streamlit

------------------------------------------------------------------------

# 1. UI Philosophy

The application should feel like a simple customer-support product.

Do not make the interface look like a complex AI research dashboard.

The user should immediately understand:

``` text
Where am I?
What can I do?
What did the AI find?
What should I do next?
```

Keep the number of visible controls low.

------------------------------------------------------------------------

# 2. Application Navigation

Use a simple sidebar.

``` text
┌──────────────────────────┐
│ Customer Support AI      │
│                          │
│ Navigation               │
│                          │
│ 💬 Chat                  │
│ 📚 Knowledge Base        │
│ 🎫 Tickets               │
│ 📊 Evaluation            │
│                          │
│ ─────────────────────    │
│ System Status            │
│ ● Knowledge Base Ready   │
└──────────────────────────┘
```

Streamlit supports simple multipage applications through a `pages/`
directory, making this structure appropriate for the MVP.

------------------------------------------------------------------------

# 3. Page Structure

Create four main pages:

``` text
Chat
Knowledge Base
Tickets
Evaluation
```

------------------------------------------------------------------------

# 4. Page 1: Customer Chat

This is the primary page.

## Layout

``` text
┌─────────────────────────────────────────────────────┐
│ Customer Support AI                                 │
│ Ask questions about the product and documentation. │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Customer                                           │
│ How do I reset my password?                        │
│                                                     │
│ AI Assistant                                       │
│ You can reset your password from Settings >        │
│ Security > Reset Password.                         │
│                                                     │
│ Sources                                             │
│ ▸ Authentication FAQ - Page 4                      │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Ask a question...                              [→]  │
└─────────────────────────────────────────────────────┘
```

Use Streamlit's chat components:

``` python
st.chat_message()
st.chat_input()
```

------------------------------------------------------------------------

# 5. Chat Welcome State

When there is no conversation:

``` text
Customer Support AI

How can we help?

Ask a question about:
• Product features
• Installation
• Troubleshooting
• Billing
• Account management

[ Ask your question below ]
```

Keep this short.

------------------------------------------------------------------------

# 6. Chat Response

Each response should have four parts:

``` text
AI Assistant

Answer:
[Answer]

Sources:
[Source 1]
[Source 2]

Was this helpful?
[Yes] [No]
```

Do not display raw vector scores to customers.

------------------------------------------------------------------------

# 7. Source Display

Sources should be visible but not dominate the interface.

Use an expander:

``` text
Sources (2)

▼ Authentication FAQ - Page 4
▼ Product Manual - Page 12
```

Inside:

``` text
Document:
Authentication FAQ

Page:
4

Section:
Password Reset
```

------------------------------------------------------------------------

# 8. Low-Confidence Response

If the system cannot answer reliably:

``` text
AI Assistant

I couldn't find enough information in the available
support documentation to answer this reliably.

Would you like to contact a support agent?

[Create Support Ticket]
```

This is preferable to displaying a guessed answer.

------------------------------------------------------------------------

# 9. Page 2: Knowledge Base

This page is for administrators.

## Layout

``` text
┌───────────────────────────────────────────────┐
│ Knowledge Base                               │
├───────────────────────────────────────────────┤
│ Upload Documents                              │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Drag and drop files here                 │ │
│ │ PDF, TXT, DOCX, MD                       │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ [Process Documents]                           │
├───────────────────────────────────────────────┤
│ Indexed Documents                             │
│                                               │
│ Document              Type     Status         │
│ product_manual.pdf    PDF      Ready          │
│ billing_faq.pdf       PDF      Ready          │
│ troubleshooting.docx DOCX     Ready          │
└───────────────────────────────────────────────┘
```

Streamlit provides `st.file_uploader()` for this interaction.

------------------------------------------------------------------------

# 10. Upload Behavior

After upload:

``` text
Uploading...
      ↓
Extracting text...
      ↓
Creating chunks...
      ↓
Generating embeddings...
      ↓
Adding to knowledge base...
      ↓
Complete
```

Use a simple progress/status display.

Do not show unnecessary technical details.

------------------------------------------------------------------------

# 11. Document Status

Use simple states:

``` text
Ready
Processing
Failed
```

Example:

``` text
product_manual.pdf       Ready
billing_faq.pdf          Ready
old_manual.pdf           Failed
```

For failed documents, provide a short reason.

------------------------------------------------------------------------

# 12. Page 3: Tickets

The ticket page should be easy for support agents to scan.

## Ticket list

``` text
┌────────────────────────────────────────────────┐
│ Support Tickets                                │
├────────────────────────────────────────────────┤
│ Filter: [All ▼]                                │
│                                                │
│ #1042   Payment failed       HIGH     OPEN     │
│ #1041   Password reset       NORMAL   OPEN     │
│ #1040   Installation issue   NORMAL   RESOLVED │
└────────────────────────────────────────────────┘
```

Use a simple table or dataframe.

------------------------------------------------------------------------

# 13. Ticket Details

When an agent opens a ticket:

``` text
┌────────────────────────────────────────────────┐
│ Ticket #1042                                   │
│ Status: OPEN                                   │
│ Category: Billing                              │
│ Priority: High                                 │
├────────────────────────────────────────────────┤
│ Customer Message                               │
│                                                │
│ I was charged twice for my subscription.       │
├────────────────────────────────────────────────┤
│ AI Analysis                                    │
│                                                │
│ Category: Billing                              │
│ Issue: Duplicate Payment                       │
├────────────────────────────────────────────────┤
│ Relevant Sources                               │
│                                                │
│ Billing FAQ - Page 8                           │
│ Refund Policy - Page 3                         │
├────────────────────────────────────────────────┤
│ Suggested Response                             │
│                                                │
│ [Editable response text area]                  │
│                                                │
│ [Send Response] [Resolve] [Escalate]           │
└────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 14. Page 4: Evaluation

This page is primarily for the developer/admin.

Keep it simple.

``` text
┌───────────────────────────────────────────────┐
│ RAG Evaluation                                │
├───────────────────────────────────────────────┤
│ Test Questions: 100                           │
│ Evaluated: 100                                │
│                                               │
│ Answer Correctness        82%                 │
│ Source Accuracy           91%                 │
│ Retrieval Success         88%                 │
│ Escalation Accuracy       94%                 │
├───────────────────────────────────────────────┤
│ Test Results                                   │
│                                               │
│ Question              Result     Source       │
│ Password reset        PASS       FAQ          │
│ Payment failure       PASS       Billing      │
│ Unknown feature       ESCALATED  None         │
└───────────────────────────────────────────────┘
```

Important:

Only display actual measured metrics.

Never hardcode an impressive score simply for presentation.

------------------------------------------------------------------------

# 15. Visual Design

Use a clean layout.

Recommended:

``` text
Background:
Light neutral

Cards:
White / slightly contrasting

Text:
Dark

Primary action:
One consistent accent color

Warnings:
Simple warning styling

Errors:
Simple error styling
```

Avoid:

-   Excessive gradients
-   Glassmorphism
-   Heavy animations
-   Large decorative graphics
-   Too many colors
-   Complex dashboards
-   Tiny text
-   Excessive icons

------------------------------------------------------------------------

# 16. Typography

Use Streamlit's default typography wherever possible.

Recommended hierarchy:

``` text
Page title
    ↓
Section heading
    ↓
Normal text
    ↓
Supporting text
```

Do not use many font sizes.

------------------------------------------------------------------------

# 17. Buttons

Buttons should use clear action names.

Good:

``` text
Upload Documents
Process Documents
Create Ticket
Resolve Ticket
Escalate
Send Response
Clear Chat
```

Avoid vague labels such as:

``` text
Go
Run
Execute
Continue
Action
```

------------------------------------------------------------------------

# 18. Sidebar

The sidebar should contain only:

``` text
App name

Navigation

Optional:
Current knowledge-base status

Optional:
Number of indexed documents
```

Do not put every setting in the sidebar.

------------------------------------------------------------------------

# 19. Admin vs Customer UI

For the MVP, keep the separation visually clear.

Customer sees:

``` text
Chat
Create Ticket
Conversation
Sources
```

Admin/support agent sees:

``` text
Knowledge Base
Tickets
Evaluation
```

Authentication can be added later.

------------------------------------------------------------------------

# 20. Loading States

Long operations should communicate progress.

Example:

``` text
Processing document...

Extracting text
✓

Creating chunks
✓

Generating embeddings
●

Saving to knowledge base
○
```

Streamlit provides status/progress components that can be used for these
operations.

------------------------------------------------------------------------

# 21. Error States

Errors should be understandable.

Bad:

``` text
ValueError: list index out of range
```

Good:

``` text
We couldn't process this document.

Please check that the file is a valid PDF and try again.
```

Technical details should be logged for developers rather than shown to
customers.

------------------------------------------------------------------------

# 22. Empty States

Every page should have a useful empty state.

### No documents

``` text
No documents have been added yet.

Upload your product documentation to create
the support knowledge base.

[Upload Documents]
```

### No tickets

``` text
No support tickets yet.
```

### No evaluation data

``` text
No evaluation results available.

Add evaluation questions and run the evaluation.
```

------------------------------------------------------------------------

# 23. Responsive Design

The UI should work reasonably on:

-   Desktop
-   Laptop
-   Tablet

Do not rely on very wide tables.

Keep important information visible without excessive horizontal
scrolling.

------------------------------------------------------------------------

# 24. Recommended Streamlit Pages

``` text
app.py
│
├── pages/
│   ├── 1_Chat.py
│   ├── 2_Knowledge_Base.py
│   ├── 3_Tickets.py
│   └── 4_Evaluation.py
```

The simple `pages/` structure is suitable for this MVP.

------------------------------------------------------------------------

# 25. Final UI Flow

### Customer

``` text
Open App
   ↓
Chat
   ↓
Ask Question
   ↓
AI Retrieves Knowledge
   ↓
Answer + Sources
   │
   ├── Helpful
   │
   └── Not Helpful
          ↓
      Create Ticket
```

### Administrator

``` text
Open Knowledge Base
       ↓
Upload Documents
       ↓
Process
       ↓
Documents Indexed
```

### Support Agent

``` text
Open Tickets
     ↓
Select Ticket
     ↓
Read Conversation
     ↓
Review AI Analysis
     ↓
Read Sources
     ↓
Edit Response
     ↓
Resolve / Escalate
```

------------------------------------------------------------------------

# 26. UI Design Rule

The entire interface should follow one principle:

> A user should understand what to do next without needing
> documentation.

The UI should be simple enough that a first-time user can:

1.  Upload a document.
2.  Ask a question.
3.  See the answer.
4.  Verify the source.
5.  Create a ticket when needed.

That is the target experience for the MVP.
