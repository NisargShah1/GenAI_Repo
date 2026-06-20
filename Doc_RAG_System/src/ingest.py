import os
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import shutil

# Configuration
DATA_PATH = "data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def get_db_path(model_type):
    return f"faiss_db_{model_type}"

def load_documents(model_type):
    """Loads all PDFs from the data directory for a specific model."""
    documents = []
    target_dir = os.path.join(DATA_PATH, model_type)
    pdf_files = glob.glob(os.path.join(target_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {target_dir}")
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
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    else:
        # Default: Local HuggingFace (Cost-effective & Fast)
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_db(chunks, embedding_function, db_path):
    """Creates (or updates) the FAISS vector store."""
    
    # Optional: Clear existing DB to start fresh (uncomment if needed)
    # if os.path.exists(db_path):
    #     shutil.rmtree(db_path)

    print("Creating Vector Database (FAISS)...")
    db = FAISS.from_documents(chunks, embedding_function)
    db.save_local(db_path)
    print(f"Vector Database saved to {db_path}")

def process_single_document(file_path, embedding_function, model_type="huggingface", progress_callback=None):
    """Processes a single document and appends it to the existing FAISS database."""
    db_path = get_db_path(model_type)
    print(f"Loading single document: {file_path}")
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    
    if not docs:
        print("No content could be loaded from the file.")
        if progress_callback:
            progress_callback(1.0, "Empty document.")
        return False
        
    chunks = split_documents(docs)
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        if progress_callback:
            progress_callback(1.0, "No chunks generated.")
        return False

    if os.path.exists(db_path):
        print(f"Loading existing Vector Database from {db_path}...")
        db = FAISS.load_local(db_path, embedding_function, allow_dangerous_deserialization=True)
    else:
        print("No existing Vector Database found. A new one will be created.")
        db = None

    print(f"Embedding {total_chunks} chunks in batches...")
    
    batch_size = 5 # Small batch size to show UI progress often
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        if db is None:
            db = FAISS.from_documents(batch, embedding_function)
        else:
            db.add_documents(batch)
            
        if progress_callback:
            progress = min(1.0, (i + len(batch)) / total_chunks)
            progress_callback(progress, f"Processed {min(i + len(batch), total_chunks)} / {total_chunks} chunks")
            
    db.save_local(db_path)
    print(f"Vector Database saved to {db_path}")
    if progress_callback:
        progress_callback(1.0, "Done!")
    return True


if __name__ == "__main__":
    # Load environment variables (for Google API Key if needed)
    from dotenv import load_dotenv
    load_dotenv()

    # Choose embedding model: 'huggingface' or 'google'
    model_type = "google"

    docs = load_documents(model_type)
    if docs:
        chunks = split_documents(docs)
        
        embedding_fn = get_embedding_function(model_type=model_type) 
        db_path = get_db_path(model_type)
        
        create_vector_db(chunks, embedding_fn, db_path)
