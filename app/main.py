from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os

from .ingestion import load_documents
from .retriever import load_vectorstore, get_relevant_docs, create_vectorstore
from .llm import get_answer

app = FastAPI(title="DocuBot - RAG Q&A System")

UPLOAD_DIR = "./data"
vectorstore = None

# Create data directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    question: str


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
    
    # If files are uploaded directly
    if files:
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"Only PDF files are allowed: {file.filename}")
            
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
    
    # Check if there are PDFs in data folder
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
    
    if not vectorstore:
        try:
            vectorstore = load_vectorstore()
        except Exception as e:
            raise HTTPException(status_code=400, detail="No documents ingested yet. Upload and ingest documents first.")
    
    relevant_docs = get_relevant_docs(vectorstore, question)
    answer = get_answer(question, relevant_docs)
    
    return {
        "question": question,
        "answer": answer,
        "sources": [{"source": doc.metadata.get("source", ""), "page": doc.metadata.get("page", "")} for doc in relevant_docs]
    }

