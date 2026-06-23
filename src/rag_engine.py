import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

DB_DIR = "data/chroma_db"

def get_embedding_model():
    """Initializes the cloud-based Google Embedding model using your existing API Key."""
    return GoogleGenerativeAIEmbeddings(
        model="text-embedding-004", 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

def initialize_vector_db():
    print("Initializing RAG Vector Database using Google Cloud API...")
    
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

    # 2. Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # 3. Connect to cloud embeddings
    embeddings = get_embedding_model()

    # 4. Save to ChromaDB
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print("✅ ChromaDB initialized successfully via Google API!")
    return vector_db

def get_retriever():
    """Returns the retriever object using the cloud embedding function."""
    embeddings = get_embedding_model()
    
    # Load the existing database structure safely
    if os.path.exists(DB_DIR):
        vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        return vector_db.as_retriever(search_kwargs={"k": 3})
    else:
        return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    initialize_vector_db()