# FastAPI - REST API Key
from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import create_rag_pipeline
import os

app = FastAPI()

qa_chain = None  # will be initialized at startup


# Initialize RAG pipeline ONLY at runtime, not at import
@app.on_event("startup")
def startup_event():
    global qa_chain

    if os.getenv("CI") == "true":
        #  CI mode: skip heavy RAG initialization
        print(" CI detected — skipping RAG initialization")
        qa_chain = None
    else:
        print("🚀 Initializing RAG pipeline...")
        qa_chain = create_rag_pipeline()

 
class Query(BaseModel):
    query: str
 
@app.get("/")
def home():
    return {"message": "RAG API Running"}
 
@app.post("/ask")
def ask(q : Query):
    result = qa_chain.invoke({"question": q.query})
    response = result['answer']
 
    sources = result.get('source_documents', [])
    return {"response": response, "sources": sources}