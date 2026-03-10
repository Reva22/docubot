from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid

from .ingestion import load_documents
from .retriever import load_vectorstore, get_relevant_docs, create_vectorstore
from .llm import get_answer

app = FastAPI(title="DocuBot - RAG Q&A System")

UPLOAD_DIR = "./data"
vectorstore = None

# In-memory session store: { session_id: [ {question, answer}, ... ] }
session_memory = {}

os.makedirs(UPLOAD_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None  # if None, a new session is created


@app.get("/")
async def root():
    return {"message": "DocuBot API is running! Go to /docs for Swagger UI"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a single PDF file"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"Uploaded {file.filename}"}


@app.post("/ingest")
async def ingest_documents(files: Optional[List[UploadFile]] = File(None)):
    """Ingest PDF documents - either from uploaded files or from data folder"""
    global vectorstore
    
    if files:
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"Only PDF files are allowed: {file.filename}")
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
    
    pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files found in data folder")
    
    chunks = load_documents(UPLOAD_DIR)
    vectorstore = create_vectorstore(chunks)
    return {"message": f"Ingested {len(chunks)} chunks from {len(pdf_files)} PDF(s)"}


@app.post("/query")
async def query(request: QueryRequest):
    """Ask a question about the documents"""
    global vectorstore

    question = request.question

    # Create a new session if none provided
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in session_memory:
        session_memory[session_id] = []

    if not vectorstore:
        try:
            vectorstore = load_vectorstore()
        except Exception:
            raise HTTPException(status_code=400, detail="No documents ingested yet. Upload and ingest documents first.")

    relevant_docs = get_relevant_docs(vectorstore, question)
    
    # Pass existing history to LLM
    answer = get_answer(question, relevant_docs, chat_history=session_memory[session_id])

    # Save this turn to session memory
    session_memory[session_id].append({
        "question": question,
        "answer": answer
    })

    return {
        "session_id": session_id,  # return to client so they can pass it in next request
        "question": question,
        "answer": answer,
        "sources": [
            {
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", "")
            }
            for doc in relevant_docs
        ]
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session"""
    if session_id in session_memory:
        del session_memory[session_id]
        return {"message": f"Session {session_id} cleared"}
    raise HTTPException(status_code=404, detail="Session not found")