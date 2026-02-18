import numpy as np
import os
import json
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from typing import List, Optional, Any

class CustomVectorStore(VectorStore):
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
        self.vectors = []
        self.documents = []

    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        embeddings = self.embedding_function.embed_documents(texts)

        print(f"Adding {embeddings} texts to CustomVectorStore")
        
        for i, text in enumerate(texts):
            self.vectors.append(np.array(embeddings[i]))
            metadata = metadatas[i] if metadatas else {}
            self.documents.append(Document(page_content=text, metadata=metadata))
        return [str(i) for i in range(len(texts))]

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        # 1. Embed the query
        query_vector = np.array(self.embedding_function.embed_query(query))
        print(f"Query vector: {query_vector}")
        # 2. Brute-force Cosine Similarity: (A · B) / (||A|| * ||B||)
        scores = []
        for v in self.vectors:
            sim = np.dot(query_vector, v) / (np.linalg.norm(query_vector) * np.linalg.norm(v))
            scores.append(sim)
            print(f"Vector: {v}, Similarity: {sim}")
        
        # 3. Get top-k indices
        top_indices = np.argsort(scores)[-k:][::-1]
        return [self.documents[i] for i in top_indices]

    @classmethod
    def from_texts(cls, texts: List[str], embedding: Any, metadatas: Optional[List[dict]] = None, **kwargs: Any):
        store = cls(embedding)
        store.add_texts(texts, metadatas)
        return store

    def save_to_disk(self, folder_path: str):
        """Save vectors and metadata to disk."""
        os.makedirs(folder_path, exist_ok=True)
        
        # Save vectors as a NumPy array
        vectors_path = os.path.join(folder_path, "vectors.npy")
        np.save(vectors_path, self.vectors)
        
        # Save metadata as JSON
        metadata_path = os.path.join(folder_path, "metadata.json")
        metadata = [doc.metadata for doc in self.documents]
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

    def load_from_disk(self, folder_path: str):
        """Load vectors and metadata from disk."""
        # Load vectors
        vectors_path = os.path.join(folder_path, "vectors.npy")
        self.vectors = np.load(vectors_path, allow_pickle=True)
        
        # Load metadata
        metadata_path = os.path.join(folder_path, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Reconstruct documents
        self.documents = [Document(page_content="", metadata=meta) for meta in metadata]
