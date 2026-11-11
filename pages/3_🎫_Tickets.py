import streamlit as st
from src.tickets import list_tickets, get_ticket, update_ticket_status
from src.rag import query_rag

st.set_page_config(page_title="Support Tickets | Agent Dashboard", page_icon="🎫", layout="wide")

st.title("🎫 Support Tickets (Agent Dashboard)")
st.caption("Review escalated customer tickets, AI analysis, retrieved context, and respond.")

# Filter
filter_status = st.selectbox("Filter Status", ["All", "OPEN", "IN_REVIEW", "RESOLVED", "ESCALATED"], index=0)
tickets = list_tickets(status_filter=filter_status)

if not tickets:
    st.info("No support tickets found matching the selected filter.")
else:
    col_list, col_detail = st.columns([1, 2])

    with col_list:
        st.subheader("Ticket Queue")
        selected_id = st.radio(
            "Select Ticket:",
            [t["id"] for t in tickets],
            format_func=lambda tid: next(f"#{t['id']} [{t['status']}] - {t['category']} ({t['priority']})" for t in tickets if t['id'] == tid)
        )

    with col_detail:
        if selected_id:
            ticket = get_ticket(selected_id)
            if ticket:
                st.subheader(f"Ticket #{ticket['id']} Details")
                
                # Header info badges
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Status:** `{ticket['status']}`")
                with c2:
                    st.write(f"**Category:** `{ticket['category']}`")
                with c3:
                    st.write(f"**Priority:** `{ticket['priority']}`")

                st.divider()

                # Customer Question
                st.markdown("### 👤 Customer Message")
                st.info(ticket["question"])

                # AI Analysis
                if ticket.get("ai_analysis"):
                    st.markdown("### 🤖 AI Analysis & Triage")
                    st.write(ticket["ai_analysis"])

                # Retrieved Context
                with st.expander("🔍 Retrieved Knowledge Context", expanded=False):
                    rag_check = query_rag(ticket["question"])
                    if rag_check.get("sources"):
                        for s in rag_check["sources"]:
                            st.markdown(f"- **{s['source']}** (Page {s['page']})")
                            if s.get("snippet"):
                                st.caption(f"> {s['snippet']}")
                    else:
                        st.caption("No directly matching documents found in knowledge base.")

                # Conversation Thread
                st.markdown("### 💬 Message Thread")
                for msg in ticket.get("messages", []):
                    role_badge = "👤 Customer" if msg["role"] == "customer" else "👨‍💼 Agent"
                    st.markdown(f"**{role_badge}** (`{msg['created_at'][:19]}`):")
                    st.write(msg["content"])

                st.divider()

                # Response drafting
                st.markdown("### ✍️ Draft Response")
                draft_default = ticket.get("suggested_response") or ""
                response_text = st.text_area("Response to Customer", value=draft_default, height=120)

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("📤 Send Response", key="btn_send"):
                        if response_text.strip():
                            update_ticket_status(ticket["id"], "IN_REVIEW", response_text.strip())
                            st.success("Response sent to customer thread!")
                            st.rerun()
                        else:
                            st.warning("Please type a response before sending.")

                with b2:
                    if st.button("✅ Mark as Resolved", key="btn_resolve"):
                        update_ticket_status(ticket["id"], "RESOLVED", response_text.strip() if response_text.strip() else None)
                        st.success("Ticket resolved!")
                        st.rerun()

                with b3:
                    if st.button("🚨 Escalate to Tier 2", key="btn_escalate"):
                        update_ticket_status(ticket["id"], "ESCALATED")
                        st.warning("Ticket escalated to Tier 2 engineering/management.")
                        st.rerun()
