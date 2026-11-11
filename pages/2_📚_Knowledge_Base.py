import streamlit as st
from pathlib import Path
from src.config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from src.document_loader import load_document
from src.chunker import chunk_text
from src.vector_store import add_chunks, delete_document, get_stats
from src.tickets import record_document, list_documents, delete_document_record

st.set_page_config(page_title="Knowledge Base | Support AI", page_icon="📚", layout="wide")

st.title("📚 Knowledge Base Management")
st.caption("Upload product manuals, FAQs, policies, and troubleshooting guides to index into ChromaDB.")

# Upload section
st.subheader("1. Upload Documents")
uploaded_files = st.file_uploader(
    "Choose documents to index (PDF, DOCX, TXT, MD)",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Process & Index Documents"):
        for file in uploaded_files:
            file_path = DOCS_DIR / file.name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            status_container = st.status(f"Processing `{file.name}`...", expanded=True)
            try:
                status_container.write("📄 Extracting text and page metadata...")
                pages = load_document(file_path)

                status_container.write("🧩 Generating chunks...")
                chunks = chunk_text(pages, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

                status_container.write("🧠 Computing embeddings and saving to ChromaDB...")
                count = add_chunks(chunks)

                record_document(file.name, file_path.suffix[1:].upper(), "Ready")
                status_container.update(label=f"✅ `{file.name}` indexed ({count} chunks)", state="complete", expanded=False)
            except Exception as e:
                record_document(file.name, file_path.suffix[1:].upper(), "Failed")
                status_container.update(label=f"❌ Failed to process `{file.name}`: {str(e)}", state="error")
        st.success("Indexing workflow complete!")
        st.rerun()

st.divider()

# Indexed documents table
st.subheader("2. Indexed Documents")
stats = get_stats()
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Documents Indexed", stats["document_count"])
with col2:
    st.metric("Total Vector Chunks", stats["chunk_count"])

db_docs = list_documents()
if not db_docs:
    st.info("No documents indexed yet. Upload documents above to build your support knowledge base.")
else:
    for doc in db_docs:
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        with c1:
            st.write(f"📄 **{doc['name']}**")
        with c2:
            st.write(f"`{doc['type']}`")
        with c3:
            st.write(f"Status: **{doc['status']}**")
        with c4:
            if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                delete_document(doc['name'])
                delete_document_record(doc['name'])
                doc_file = DOCS_DIR / doc['name']
                if doc_file.exists():
                    doc_file.unlink()
                st.toast(f"Deleted {doc['name']}")
                st.rerun()
