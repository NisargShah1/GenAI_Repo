import os
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder

# Configuration
DB_PATH = "faiss_db"

class RAGEngine:
    def __init__(self, embedding_model="huggingface", llm_model="gemini-2.5-pro"):
        self.embedding_model_type = embedding_model
        
        # 1. Setup Embeddings
        if embedding_model == "google":
            self.embedding_fn = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        else:
            self.embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        # 2. Load Vector DB
        if os.path.exists(DB_PATH):
            self.vector_db = FAISS.load_local(DB_PATH, self.embedding_fn, allow_dangerous_deserialization=True)
            self.vector_retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
            
            # 👉 Load all docs for BM25
            self.all_docs = self.vector_db.docstore._dict.values()
            self.bm25_retriever = BM25Retriever.from_documents(list(self.all_docs))
            self.bm25_retriever.k = 5

        else:
            raise FileNotFoundError(f"Vector DB not found at {DB_PATH}. Run ingest.py first.")

        # 3. Setup Reranker (Cross Encoder)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        # 4. Setup LLM
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.3)

        # 5. Prompt
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful AI assistant for a research organization. 
        Answer the question based ONLY on the following context:

        {context}

        Question: {question}

        If the answer is not in the context, say "I don't have enough information in the provided documents to answer that."
        Do not hallucinate.

        Answer:
        """)

    def format_docs(self, docs):
        return "\n\n".join([d.page_content for d in docs])

    # Hybrid retrieval
    def hybrid_retrieve(self, query):
        vector_docs = self.vector_retriever.invoke(query)
        bm25_docs = self.bm25_retriever.invoke(query)

        # Merge + deduplicate
        seen = set()
        combined = []
        for doc in vector_docs + bm25_docs:
            if doc.page_content not in seen:
                combined.append(doc)
                seen.add(doc.page_content)

        return combined

    # Rerank
    def rerank(self, query, docs, top_k=5):
        pairs = [(query, doc.page_content) for doc in docs]
        scores = self.reranker.predict(pairs)

        scored_docs = list(zip(docs, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored_docs[:top_k]]

    def query(self, question):
        # 1. Hybrid Retrieval
        hybrid_docs = self.hybrid_retrieve(question)

        # 2. Rerank
        top_docs = self.rerank(question, hybrid_docs, top_k=5)

        # 3. Generate
        chain = (
            {
                "context": lambda x: self.format_docs(top_docs),
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke(question)

        return {
            "answer": response,
            "source_documents": top_docs
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