import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Create a folder to store the local vector database
DB_DIR = "data/chroma_db"

def initialize_vector_db():
    print("Initializing RAG Vector Database...")
    
    # 1. Load the knowledge and history files
    documents = []
    
    knowledge_path = "data/gold_knowledge.txt"
    if os.path.exists(knowledge_path):
        loader = TextLoader(knowledge_path, encoding="utf-8")
        documents.extend(loader.load())
        
    history_path = "data/report_history.txt"
    if os.path.exists(history_path):
        loader = TextLoader(history_path, encoding="utf-8")
        documents.extend(loader.load())

    if not documents:
        print("No documents found to process.")
        return None

    # 2. Split the text into manageable chunks for the AI
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # 3. Create Embeddings (Converts text to math vectors)
    # Using an open-source, lightweight model that runs locally
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Save to ChromaDB
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print("✅ ChromaDB initialized successfully!")
    return vector_db

def get_retriever():
    """Returns the retriever object to be used by our assistant."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the existing database
    if os.path.exists(DB_DIR):
        vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        # Search for the top 3 most relevant chunks
        return vector_db.as_retriever(search_kwargs={"k": 3})
    else:
        return None

if __name__ == "__main__":
    # Run this file directly to build the database for the first time
    initialize_vector_db()