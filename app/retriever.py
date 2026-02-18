from langchain_huggingface import HuggingFaceEmbeddings
from app.customvectorstore import CustomVectorStore

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

def create_vectorstore(chunks, persist_dir="./vectorstore"):
    embeddings = get_embeddings()
    vectorstore = CustomVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectorstore

def load_vectorstore(persist_dir="./vectorstore"):
    embeddings = get_embeddings()
    return CustomVectorStore(persist_directory=persist_dir, embedding_function=embeddings)

def get_relevant_docs(vectorstore, query: str, k: int = 3):
    return vectorstore.similarity_search(query, k=k)