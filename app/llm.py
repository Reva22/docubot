from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

def get_answer(query: str, context_docs: list):
    context = "\n\n".join([doc.page_content for doc in context_docs])
    
    prompt = PromptTemplate.from_template("""
    You are a helpful assistant. Answer the question based only on the provided context.
    If the answer is not in the context, say "I don't have enough information to answer this."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})
    return response.content