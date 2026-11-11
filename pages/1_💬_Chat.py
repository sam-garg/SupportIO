import streamlit as st
from src.rag import query_rag
from src.tickets import create_ticket, save_feedback
from src.llm import analyze_ticket_question, render_model_selector

st.set_page_config(page_title="Customer Chat | Support AI", page_icon="💬", layout="centered")

with st.sidebar:
    render_model_selector()

st.title("💬 Customer Support Assistant")
st.caption("Ask any question about our products, billing, installation, or troubleshooting.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message if empty
if not st.session_state.messages:
    st.info(
        "👋 **How can we help you today?**\n\n"
        "Feel free to ask about:\n"
        "- Product features & configuration\n"
        "- Installation guides\n"
        "- Troubleshooting & error codes\n"
        "- Billing & account management"
    )

# Render chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display sources if present
        if msg.get("sources"):
            with st.expander(f"📚 Sources ({len(msg['sources'])})", expanded=False):
                for src in msg["sources"]:
                    st.markdown(f"**Document:** `{src['source']}` (Page {src['page']})")
                    if src.get("snippet"):
                        st.caption(f"> \"{src['snippet']}\"")
        
        # Escalation CTA button
        if msg.get("is_escalated") and not msg.get("ticket_created"):
            if st.button("🎫 Create Support Ticket", key=f"esc_btn_{idx}"):
                with st.spinner("Creating support ticket for our human team..."):
                    analysis = analyze_ticket_question(msg.get("user_query", ""))
                    tid = create_ticket(
                        question=msg.get("user_query", ""),
                        customer_name="Customer",
                        category=analysis.get("category", "General"),
                        priority=analysis.get("priority", "Normal"),
                        ai_analysis=analysis.get("analysis", ""),
                        suggested_response=analysis.get("suggested_response", "")
                    )
                    msg["ticket_created"] = tid
                    st.success(f"Ticket **#{tid}** created successfully! Our human support team will review it.")
                    st.rerun()
        elif msg.get("ticket_created"):
            st.success(f"✅ Escalated to support agent (Ticket **#{msg['ticket_created']}**)")

        # Feedback buttons for assistant answers
        if msg["role"] == "assistant" and not msg.get("feedback_given"):
            col1, col2, _ = st.columns([1, 1, 4])
            with col1:
                if st.button("👍 Helpful", key=f"thumb_up_{idx}"):
                    save_feedback(msg.get("user_query", ""), msg["content"], "helpful")
                    msg["feedback_given"] = True
                    st.toast("Thank you for your feedback!")
                    st.rerun()
            with col2:
                if st.button("👎 Not helpful", key=f"thumb_down_{idx}"):
                    save_feedback(msg.get("user_query", ""), msg["content"], "not_helpful")
                    msg["feedback_given"] = True
                    st.toast("Thank you for your feedback!")
                    st.rerun()

# User input
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate RAG response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            rag_res = query_rag(prompt)
            answer = rag_res["answer"]
            sources = rag_res["sources"]
            is_escalated = rag_res["is_escalated"]

            st.markdown(answer)
            if sources:
                with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                    for src in sources:
                        st.markdown(f"**Document:** `{src['source']}` (Page {src['page']})")
                        if src.get("snippet"):
                            st.caption(f"> \"{src['snippet']}\"")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "is_escalated": is_escalated,
                "user_query": prompt
            })
            st.rerun()
