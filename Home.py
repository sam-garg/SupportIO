import streamlit as st
from src.vector_store import get_stats
from src.llm import render_model_selector

st.set_page_config(
    page_title="Home | Customer Support AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Customer Support AI Platform")
st.markdown("An AI-powered customer support system with grounded document retrieval (RAG) and human escalation.")

col1, col2, col3 = st.columns(3)

stats = get_stats()

with col1:
    st.metric(label="📚 Indexed Documents", value=stats["document_count"])

with col2:
    st.metric(label="🧩 Knowledge Chunks", value=stats["chunk_count"])

with col3:
    status_icon = "🟢 Ready" if stats["document_count"] > 0 else "🟡 Needs Documents"
    st.metric(label="⚡ System Status", value=status_icon)

st.divider()

st.subheader("🧭 Navigation")
c1, c2 = st.columns(2)

with c1:
    st.info("### 💬 [Customer Chat](/Chat)\nAsk questions with automatic source citations and escalation.")
    st.info("### 📚 [Knowledge Base](/Knowledge_Base)\nUpload PDF, DOCX, TXT, and Markdown product docs.")

with c2:
    st.info("### 🎫 [Support Tickets](/Tickets)\nReview escalated tickets, edit responses, and resolve.")
    st.info("### 📊 [RAG Evaluation](/Evaluation)\nRun benchmarks to measure real retrieval and escalation metrics.")

with st.sidebar:
    render_model_selector()
    st.subheader("System Information")
    st.caption("Vector Store: ChromaDB")
    st.caption("Embeddings: Sentence-Transformers")
    if stats["documents"]:
        st.write("**Active Knowledge Base:**")
        for doc in stats["documents"]:
            st.markdown(f"- 📄 `{doc}`")
