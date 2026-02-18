import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.customvectorstore import CustomVectorStore
from langchain_core.documents import Document
import numpy as np
# Mock embedding function
class MockEmbeddingFunction:
    def embed_documents(self, texts):
        # Return a simple embedding (e.g., length of text as a vector)
        return [[len(text)] for text in texts]
    
    def embed_query(self, query):
        # Return a simple embedding for the query
        return [len(query)]

# Initialize the CustomVectorStore
embedding_function = MockEmbeddingFunction()
vector_store = CustomVectorStore(embedding_function)

# Test add_texts
texts = ["hello", "world", "test", "vector"]
metadatas = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
vector_store.add_texts(texts, metadatas)

# Verify vectors and documents
assert len(vector_store.vectors) == len(texts)
assert len(vector_store.documents) == len(texts)

# Test similarity_search
query = "hello world"
results = vector_store.similarity_search(query, k=2)

# Verify results
assert len(results) == 2
assert isinstance(results[0], Document)

# Test from_texts
new_store = CustomVectorStore.from_texts(texts, embedding_function, metadatas)
assert len(new_store.documents) == len(texts)