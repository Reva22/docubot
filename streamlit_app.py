import streamlit as st
import requests

st.set_page_config(page_title="DocuBot", page_icon="📄")
st.title("📄 DocuBot - Ask Your Documents")
st.caption("Upload PDFs and ask questions using AI")

API_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for upload
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        files = []
        for uploaded_file in uploaded_files:
            files.append(
                ("files", (uploaded_file.name, uploaded_file.getvalue(), "application/pdf"))
            )
        
        response = requests.post(f"{API_URL}/ingest", files=files)
        if response.status_code == 200:
            st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)")
        else:
            st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")

    st.divider()

    # New chat button clears session
    if st.button("🗑️ New Chat", use_container_width=True):
        if st.session_state.session_id:
            requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
        st.session_state.session_id = None
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload PDFs**: Use the sidebar to upload one or more PDF documents
        2. **Wait for processing**: Documents will be processed and indexed
        3. **Ask questions**: Type your question and get AI-powered answers
        4. **Follow-up**: Ask follow-up questions — DocuBot remembers the conversation
        5. **New Chat**: Click "New Chat" to start a fresh session
        """)

# Display chat history
st.divider()
for turn in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        if turn.get("sources"):
            with st.expander("📚 Sources"):
                for i, src in enumerate(turn["sources"], 1):
                    source = src.get("source", "")
                    page = src.get("page", "")
                    st.write(f"{i}. `{source}`  —  Page {page}" if page else f"{i}. `{source}`")

# Chat input at bottom
question = st.chat_input("💬 Ask a question about your documents...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/query",
                json={
                    "question": question,
                    "session_id": st.session_state.session_id
                }
            )

            if response.status_code == 200:
                data = response.json()

                # Save session_id from first response
                if not st.session_state.session_id:
                    st.session_state.session_id = data["session_id"]

                st.write(data["answer"])

                if data.get("sources"):
                    with st.expander("📚 Sources"):
                        for i, src in enumerate(data["sources"], 1):
                            source = src.get("source", "")
                            page = src.get("page", "")
                            st.write(f"{i}. `{source}`  —  Page {page}" if page else f"{i}. `{source}`")

                # Save to local chat history for display
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": data["answer"],
                    "sources": data.get("sources", [])
                })

            else:
                st.error(response.json().get("detail", "Error getting answer"))