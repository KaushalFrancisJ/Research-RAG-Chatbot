import uuid
import os
import streamlit as st
import requests

# Prefer st.secrets (Streamlit Cloud), fall back to env var, then localhost for local dev
API_BASE = st.secrets.get("API_BASE", os.getenv("API_BASE", "http://localhost:8000/api"))


def get_error_message(response: requests.Response) -> str:
    """Safely extract an error message from any response, JSON or plain text."""
    try:
        return response.json().get("detail", response.text)
    except Exception:
        return response.text or f"HTTP {response.status_code}"


# Generate a session ID once per browser session and persist it across reruns.
# A page refresh keeps the same st.session_state, so the ID survives reruns
# but is brand-new for every fresh tab or browser session.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

SESSION_HEADERS = {"X-Session-Id": st.session_state.session_id}

st.title("RAG Chatbot")

# ── 1. Upload & Chunk ──────────────────────────────────────────────────────────
st.header("1. Upload PDF")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if st.button("Upload & Chunk"):
    if not uploaded_file:
        st.warning("Please select a PDF file first.")
    else:
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{API_BASE}/upload",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    headers=SESSION_HEADERS,
                )
                if response.ok:
                    data = response.json()
                    st.session_state.pdf_uploaded = True
                    st.success(f"✅ **{data['filename']}** processed into **{data['chunks']}** chunks.")
                else:
                    st.error(f"Error: {get_error_message(response)}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")

st.divider()

# ── 2. Generation ──────────────────────────────────────────────────────────────
st.header("2. Ask a Question")

query = st.text_input("Your question")
k_gen = st.slider("Number of chunks to retrieve", 1, 10, 5, key="k_gen")
if st.button("Generate Answer"):
    if not query:
        st.warning("Please enter a question.")
    elif not st.session_state.get("pdf_uploaded"):
        st.warning("Please upload a PDF first.")
    else:
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    f"{API_BASE}/generate",
                    json={"query": query, "k": k_gen},
                    headers=SESSION_HEADERS,
                )
                if response.ok:
                    data = response.json()
                    st.subheader("Answer")
                    st.write(data["answer"])
                    with st.expander("Retrieved Chunks"):
                        for i, chunk in enumerate(data["chunks"], 1):
                            st.markdown(f"**{i}. {chunk['source']} (Page {chunk['page']})**")
                            st.caption(chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else ""))
                else:
                    st.error(f"Error: {get_error_message(response)}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")

st.divider()

# ── 3. Evaluation ──────────────────────────────────────────────────────────────
st.header("3. Evaluate RAG Quality")

st.markdown(
    "Runs a fixed set of diagnostic questions against the indexed document and scores "
    "each answer using a Gemini judge on two metrics:"
)
st.markdown(
    "| Metric | Scale | Description |\n"
    "|---|---|---|\n"
    "| **Faithfulness** | 1 – 5 | Is the answer factually grounded in the retrieved context? |\n"
    "| **Answer Relevancy** | 1 – 5 | Does the answer actually address the question? |"
)
st.caption(
    "Questions used: main topic · key findings · problem addressed · "
    "methods described · limitations mentioned"
)

if st.button("Evaluate"):
    if not st.session_state.get("pdf_uploaded"):
        st.warning("Please upload a PDF first.")
    else:
        with st.spinner("Running evaluation across all questions..."):
            try:
                response = requests.post(
                    f"{API_BASE}/evaluate",
                    headers=SESSION_HEADERS,
                )
                if response.ok:
                    results = response.json()["results"]

                    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
                    avg_rel = sum(r["answer_relevancy"] for r in results) / len(results)
                    col1, col2 = st.columns(2)
                    col1.metric("Avg Faithfulness", f"{avg_faith:.1f} / 5")
                    col2.metric("Avg Answer Relevancy", f"{avg_rel:.1f} / 5")

                    st.subheader("Results")
                    for r in results:
                        faith_bar = "🟩" * r["faithfulness"] + "⬜" * (5 - r["faithfulness"])
                        rel_bar   = "🟩" * r["answer_relevancy"] + "⬜" * (5 - r["answer_relevancy"])
                        with st.expander(f"❓ {r['question']}"):
                            st.markdown(f"**Answer:** {r['answer']}")
                            st.markdown("---")
                            st.markdown(f"**Faithfulness:** {faith_bar} {r['faithfulness']}/5")
                            st.caption(r["faithfulness_reason"])
                            st.markdown(f"**Answer Relevancy:** {rel_bar} {r['answer_relevancy']}/5")
                            st.caption(r["answer_relevancy_reason"])

                    st.subheader("Score Summary")
                    table_data = {
                        "Question": [r["question"] for r in results],
                        "Faithfulness": [f"{r['faithfulness']} / 5" for r in results],
                        "Answer Relevancy": [f"{r['answer_relevancy']} / 5" for r in results],
                    }
                    st.table(table_data)

                else:
                    st.error(f"Error: {get_error_message(response)}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")
