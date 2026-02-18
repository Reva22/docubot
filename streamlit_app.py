import streamlit as st
import requests

st.set_page_config(page_title="DocuBot", page_icon="📄")
st.title("📄 DocuBot - Ask Your Documents")
st.caption("Upload PDFs and ask questions using AI")

API_URL = "http://localhost:8000"

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

# Main chat area
st.divider()
question = st.text_input("💬 Ask a question about your documents:")

if st.button("Get Answer", type="primary"):
    if not question:
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/query", 
                json={"question": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "warning":
                    st.warning(data["message"])
                else:
                    st.subheader("Answer")
                    st.write(data["answer"])
                    
                    if data.get("sources"):
                        with st.expander("📚 Sources"):
                            for i, src in enumerate(data["sources"], 1):
                                st.write(f"{i}. {src[:200]}..." if len(src) > 200 else f"{i}. {src}")
            else:
                st.error(response.json().get("detail", "Error getting answer"))

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Upload PDFs**: Use the sidebar to upload one or more PDF documents
    2. **Wait for processing**: The documents will be processed and indexed
    3. **Ask questions**: Type your question in the text box and get AI-powered answers
    """)

