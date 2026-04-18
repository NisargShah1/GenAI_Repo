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
    
    embedding_option = st.selectbox(
        "Embedding Model",
        ("huggingface", "google"),
        index=0,
        help="Select 'google' for better quality (requires API Key), 'huggingface' for local/fast."
    )
    
    st.divider()
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    st.divider()
    st.header(f"Uploaded Documents ({embedding_option})")
    data_folder = os.path.join("data", embedding_option)
    if os.path.exists(data_folder):
        uploaded_files_list = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]
        if uploaded_files_list:
            for f in uploaded_files_list:
                st.markdown(f"- {f}")
        else:
            st.write("No documents uploaded yet.")
    else:
        st.write("No documents uploaded yet.")

    if uploaded_file is not None:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            st.session_state.last_uploaded = uploaded_file.name
            
            # Save file
            import os
            from src.ingest import process_single_document, get_embedding_function
            
            os.makedirs(data_folder, exist_ok=True)
            save_path = os.path.join(data_folder, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.success(f"Saved {uploaded_file.name} to {data_folder}.")
            
            # Process File
            st.info("Processing document...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
                
            try:
                embedding_fn = get_embedding_function(embedding_option)
                process_single_document(save_path, embedding_fn, embedding_option, update_progress)
                st.success("Document processed and added to the Knowledge Base!")
                # Delete the old engine instance so we reload the updated DB
                if 'engine' in st.session_state:
                    del st.session_state.engine
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "expander_content" in message:
            with st.expander("Show Document Retrieval Details"):
                st.markdown(message["expander_content"])

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
            if embedding_option == "google" and not os.environ.get("GOOGLE_API_KEY"):
                st.error("Please ensure your Google API Key is set in the .env file.")
                st.stop()
                
            # Initialize Engine and keep in session state so we don't load it on every keystroke/interaction
            if "engine" not in st.session_state:
                st.session_state.engine = RAGEngine(embedding_model=embedding_option)
            engine = st.session_state.engine
            
            with st.spinner("Thinking..."):
                result = engine.query(prompt)
                
            response_text = result["answer"]
            message_placeholder.markdown(response_text)
            
            expander_markdown = ""
            if result.get("source_documents"):
                def format_docs_md(title, docs):
                    md = f"**{title}** ({len(docs)} documents)\n\n"
                    if not docs:
                        return md + "None\n\n"
                    for i, doc in enumerate(docs):
                        src = f"{os.path.basename(doc.metadata.get('source', 'Unknown'))} (Page {doc.metadata.get('page', '?')})"
                        snippet = doc.page_content.replace('\n', ' ')[:100] + '...'
                        md += f"{i+1}. **{src}** - _{snippet}_\n"
                    return md + "\n"

                detail_md = ""
                queries = result.get("queries_run", [])
                if queries:
                    detail_md += f"**0. Generated Search Queries** ({len(queries)} queries)\n\n"
                    for i, q in enumerate(queries):
                        detail_md += f"{i+1}. `{q}`\n"
                    detail_md += "\n"
                    
                detail_md += format_docs_md("1. Vector DB Retrieval", result.get("raw_vector_docs", []))
                detail_md += format_docs_md("2. Keyword (BM25) Retrieval", result.get("raw_bm25_docs", []))
                detail_md += format_docs_md("3. After Deduplication", result.get("deduplicated_docs", []))
                detail_md += format_docs_md("4. Final Reranked (Context to LLM)", result.get("source_documents", []))
                
                expander_markdown = detail_md
                with st.expander("Show Document Retrieval Details"):
                    st.markdown(expander_markdown)
            
            # Add assistant response to history
            msg_data = {"role": "assistant", "content": response_text}
            if expander_markdown:
                msg_data["expander_content"] = expander_markdown
            st.session_state.messages.append(msg_data)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
