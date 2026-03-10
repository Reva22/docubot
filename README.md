# DocuBot

An AI-powered document Q&A system built with FastAPI, LangChain, and ChromaDB.

![ScreenRecording2026-03-11at12 16 12AM-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/b7a26e3c-13bc-4cfe-b504-e5f488b28a47)

## Project Structure

```
docubot/
├── app/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration settings
│   ├── ingestion.py     # Document processing
│   ├── retriever.py     # Vector search
│   └── llm.py           # LLM response generation
├── data/                 # Store PDFs here
├── vectorstore/          # ChromaDB persistent storage
├── venv/                 # Virtual environment
├── .env                  # Environment variables
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
├── streamlit_app.py      # Streamlit UI
└── README.md            # This file
```

## Setup

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google API Key:**
   - Open `.env` file
   - Add your Google API key: `GOOGLE_API_KEY=your_api_key_here`
   - Get your API key from: https://aistudio.google.com/app/apikey

## Running the Application

### Option 1: FastAPI Server
```bash
uvicorn app.main:app --reload
```
The API will be available at: http://localhost:8000

### Option 2: Streamlit UI
```bash
streamlit run streamlit_app.py
```
The Streamlit app will open at: http://localhost:8501

## API Endpoints

- **GET /** - Root endpoint
- **POST /upload** - Upload a single PDF file
- **POST /ingest** - Ingest PDF documents from data folder or uploaded files
- **POST /query** - Ask questions about documents

## Usage Example

### Using FastAPI

1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Upload a document:
   ```bash
   curl -X POST -F "file=@document.pdf" http://localhost:8000/upload
   ```

3. Ingest documents:
   ```bash
   curl -X POST http://localhost:8000/ingest
   ```

4. Ask a question:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"question": "What is this document about?"}' \
     http://localhost:8000/query
   ```

### Using Streamlit

Simply run:
```bash
streamlit run streamlit_app.py
```

Then:
1. Upload PDF documents using the sidebar
2. Wait for processing
3. Type your question and get AI-powered answers

## Development

- FastAPI documentation: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

