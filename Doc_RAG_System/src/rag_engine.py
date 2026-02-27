import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Configuration
DB_PATH = "faiss_db"

class RAGEngine:
    def __init__(self, embedding_model="huggingface", llm_model="gemini-pro"):
        """Initializes the RAG Engine."""
        self.embedding_model_type = embedding_model
        
        # 1. Setup Embeddings
        if embedding_model == "google":
            self.embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        else:
            self.embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        # 2. Load Vector DB
        if os.path.exists(DB_PATH):
            self.vector_db = FAISS.load_local(DB_PATH, self.embedding_fn, allow_dangerous_deserialization=True)
            self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5}) # Fetch top 5
        else:
            raise FileNotFoundError(f"Vector DB not found at {DB_PATH}. Run ingest.py first.")

        # 3. Setup LLM
        # Using Gemini Pro via LangChain
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.3)

        # 4. Setup Prompt
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful AI assistant for a research organization. 
        Answer the question based ONLY on the following context:

        {context}

        Question: {question}

        If the answer is not in the context, say "I don't have enough information in the provided documents to answer that."
        Do not halluncinate.

        Answer:
        """)

    def format_docs(self, docs):
        """Formats retrieved documents for the prompt."""
        return "\n\n".join([d.page_content for d in docs])

    def query(self, question):
        """Executes the RAG pipeline."""
        
        # 1. Retrieve
        retrieved_docs = self.retriever.get_relevant_documents(question)
        
        # 2. Generate
        chain = (
            {"context": lambda x: self.format_docs(retrieved_docs), "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        response = chain.invoke(question)
        
        return {
            "answer": response,
            "source_documents": retrieved_docs
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        engine = RAGEngine()
        result = engine.query("What are the key findings?")
        print("Answer:", result["answer"])
        print("\nSources:")
        for doc in result["source_documents"]:
            print(f"- {doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', '?')})")
    except Exception as e:
        print(f"Error: {e}")
