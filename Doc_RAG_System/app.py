import streamlit as st
import os
from src.rag_engine import RAGEngine
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Doc RAG System", layout="wide")

st.title("📄 Document RAG System")
st.markdown("Ask questions based on your loaded PDF documents.")

# Sidebar: Settings
with st.sidebar:
    st.header("Settings")
    
    api_key = st.text_input("Google API Key", type="password", help="Required for Gemini Pro")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    embedding_option = st.selectbox(
        "Embedding Model",
        ("huggingface", "google"),
        index=0,
        help="Select 'google' for better quality (requires API Key), 'huggingface' for local/fast."
    )
    
    st.divider()
    st.info("Ensure you have run `python src/ingest.py` to load documents first.")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Enter your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Initialize Engine (Lazy load to pick up latest settings)
            if not os.environ.get("GOOGLE_API_KEY"):
                st.error("Please enter your Google API Key in the sidebar.")
                st.stop()
                
            engine = RAGEngine(embedding_model=embedding_option)
            
            with st.spinner("Thinking..."):
                result = engine.query(prompt)
                
            response_text = result["answer"]
            
            # Append Sources
            sources_text = "\n\n**Sources:**\n"
            seen_sources = set()
            for doc in result["source_documents"][:3]: # Top 3 unique sources
                src = f"{os.path.basename(doc.metadata.get('source', 'Unknown'))} (Page {doc.metadata.get('page', '?')})"
                if src not in seen_sources:
                    sources_text += f"- {src}\n"
                    seen_sources.add(src)
            
            full_response = response_text + sources_text
            message_placeholder.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
