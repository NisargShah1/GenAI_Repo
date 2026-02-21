import os
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import shutil

# Configuration
DATA_PATH = "data"
DB_PATH = "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def load_documents():
    """Loads all PDFs from the data directory."""
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {DATA_PATH}")
        return []

    print(f"Found {len(pdf_files)} PDFs. Loading...")
    
    for file_path in pdf_files:
        try:
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {file_path} ({len(docs)} pages)")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return documents

def split_documents(documents):
    """Splits documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def get_embedding_function(model_type="huggingface"):
    """Returns the embedding function based on preference."""
    if model_type == "google":
        # Requires GOOGLE_API_KEY in environment
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    else:
        # Default: Local HuggingFace (Cost-effective & Fast)
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_db(chunks, embedding_function):
    """Creates (or updates) the Chroma vector store."""
    
    # Optional: Clear existing DB to start fresh (uncomment if needed)
    # if os.path.exists(DB_PATH):
    #     shutil.rmtree(DB_PATH)

    print("Creating Vector Database...")
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_function, 
        persist_directory=DB_PATH
    )
    db.persist()
    print(f"Vector Database saved to {DB_PATH}")

if __name__ == "__main__":
    # Load environment variables (for Google API Key if needed)
    from dotenv import load_dotenv
    load_dotenv()

    docs = load_documents()
    if docs:
        chunks = split_documents(docs)
        
        # Choose embedding model: 'huggingface' or 'google'
        embedding_fn = get_embedding_function(model_type="huggingface") 
        
        create_vector_db(chunks, embedding_fn)
