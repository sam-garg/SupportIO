import streamlit as st
import json
from src.evaluation import run_evaluation, load_eval_questions, EVAL_FILE

st.set_page_config(page_title="RAG Evaluation | Support AI", page_icon="📊", layout="wide")

st.title("📊 RAG Evaluation & Quality Benchmark")
st.caption("Measure retrieval success rate, escalation accuracy, and response latency on ground-truth benchmark questions.")

# Current benchmark stats
questions = load_eval_questions()
st.write(f"**Benchmark Dataset:** `{len(questions)} test questions loaded`")

if st.button("▶️ Run Evaluation Benchmark", type="primary"):
    with st.spinner("Running evaluation across all test questions..."):
        metrics = run_evaluation()
        st.session_state.eval_results = metrics

if "eval_results" in st.session_state:
    res = st.session_state.eval_results

    st.subheader("Measured Quality Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Test Questions", res["total"])
    with m2:
        st.metric("Retrieval Success Rate", f"{res['retrieval_success_rate']}%")
    with m3:
        st.metric("Escalation Accuracy", f"{res['escalation_accuracy']}%")
    with m4:
        st.metric("Avg Latency", f"{res['avg_latency_sec']}s")

    st.divider()
    st.subheader("Detailed Evaluation Breakdown")
    for d in res["details"]:
        status_badge = "✅ PASS" if (d["retrieval_pass"] and d["escalation_pass"]) else "⚠️ REVIEW"
        with st.expander(f"{status_badge} - {d['question']} ({d['latency']}s)"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Expected Source:** `{d['expected_source']}`")
                st.write(f"**Retrieved Sources:** `{d['retrieved_sources']}`")
                st.write(f"**Retrieval Passed:** `{'Yes' if d['retrieval_pass'] else 'No'}`")
            with c2:
                st.write(f"**Should Escalate:** `{'Yes' if d['expected_escalate'] else 'No'}`")
                st.write(f"**Actually Escalated:** `{'Yes' if d['is_escalated'] else 'No'}`")
                st.write(f"**Escalation Passed:** `{'Yes' if d['escalation_pass'] else 'No'}`")

st.divider()

# Add benchmark question form
with st.expander("➕ Add New Evaluation Benchmark Question"):
    new_q = st.text_input("Test Question", placeholder="e.g. How to change billing credit card?")
    new_src = st.text_input("Expected Source Document", placeholder="e.g. billing_guide.pdf (or 'none' if out of scope)")
    should_esc = st.checkbox("Should this question trigger human escalation?", value=False)
    
    if st.button("💾 Save Question"):
        if new_q.strip() and new_src.strip():
            questions.append({
                "question": new_q.strip(),
                "expected_source": new_src.strip(),
                "should_escalate": should_esc
            })
            with open(EVAL_FILE, "w", encoding="utf-8") as f:
                json.dump(questions, f, indent=2)
            st.success("Test question saved!")
            st.rerun()
        else:
            st.warning("Please provide both question and expected source.")
