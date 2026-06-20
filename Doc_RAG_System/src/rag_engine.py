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

class RAGEngine:
    def __init__(self, embedding_model="huggingface", llm_model="gemini-2.5-pro"):
        self.embedding_model_type = embedding_model
        db_path = f"faiss_db_{embedding_model}"
        
        # 1. Setup Embeddings
        if embedding_model == "google":
            self.embedding_fn = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        else:
            self.embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        # 2. Load Vector DB
        if os.path.exists(db_path):
            self.vector_db = FAISS.load_local(db_path, self.embedding_fn, allow_dangerous_deserialization=True)
            self.vector_retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
            
            # 👉 Load all docs for BM25
            self.all_docs = self.vector_db.docstore._dict.values()
            self.bm25_retriever = BM25Retriever.from_documents(list(self.all_docs))
            self.bm25_retriever.k = 10

        else:
            raise FileNotFoundError(f"Vector DB not found at {db_path}. Run ingest.py first.")

        # 3. Setup Reranker (Cross Encoder)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        # 4. Setup LLM
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.3)

        # 5. Prompts
        self.prompt = ChatPromptTemplate.from_template("""
        You are an intelligent, helpful AI assistant for a research organization.
        You have been provided with some context from relevant documents.

        Context:
        {context}

        User Question: {question}

        Instructions:
        1. Try to answer the question using the provided context primarily.
        2. If the context does not contain the answer, or only partially contains the answer, use your own general knowledge to answer or supplement the information.
        3. If you use your own knowledge, subtly mention that the information comes from your general knowledge and not the specific documents.
        4. If you cannot answer the question at all even with your knowledge, politely state that you do not have enough information.
        
        Answer:
        """)
        
        self.decomposer_prompt = ChatPromptTemplate.from_template("""
        Analyze the following user query.
        Determine if it is a simple conversational greeting (e.g., "hi", "hello", "how are you", "good morning") where the user does not expect information.
        
        If it is a simple conversational greeting, respond exactly with: GREETING
        
        Otherwise, if it asks a substantive question, your task is to decompose the query into up to 3 sub queries that break down the user's question into logical component parts to maximize retrieval from a vector database. Write each sub query on a new line. Do not number them or include any other text.

        Example:
        Query: compare gemini and gpt models
        Output:
        give details about gemini model
        give details about gpt models
        gemini and gpt model architecture and performance
        
        User Query: {question}
        """)

    def decompose_query(self, question):
        response = (self.decomposer_prompt | self.llm | StrOutputParser()).invoke({"question": question})
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if len(lines) == 1 and lines[0] == "GREETING":
            return {"type": "greeting"}
        return {"type": "search", "queries": lines}

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

        return vector_docs, bm25_docs, combined

    # Rerank
    def rerank(self, query, docs, top_k=5):
        pairs = [(query, doc.page_content) for doc in docs]
        scores = self.reranker.predict(pairs)

        scored_docs = list(zip(docs, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored_docs[:top_k]]

    def query(self, question):
        # 0. Analyze & Decompose Query
        analysis = self.decompose_query(question)
        
        if analysis["type"] == "greeting":
            # Handle greeting directly
            response = self.llm.invoke("The user sent a greeting: " + question + ". Respond politely.")
            return {
                "answer": response.content,
                "queries_run": [],
                "raw_vector_docs": [],
                "raw_bm25_docs": [],
                "deduplicated_docs": [],
                "source_documents": []
            }
            
        # 1. Multi-Query Hybrid Retrieval
        queries_to_run = analysis["queries"] if analysis["queries"] else [question]
        
        all_vector_docs = []
        all_bm25_docs = []
        all_combined_docs = []
        seen_contents = set()
        
        for q in queries_to_run:
            v_docs, b_docs, combined = self.hybrid_retrieve(q)
            all_vector_docs.extend(v_docs)
            all_bm25_docs.extend(b_docs)
            
            for doc in combined:
                if doc.page_content not in seen_contents:
                    all_combined_docs.append(doc)
                    seen_contents.add(doc.page_content)

        # 2. Rerank
        top_docs = self.rerank(question, all_combined_docs, top_k=10)

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
            "queries_run": queries_to_run,
            "raw_vector_docs": all_vector_docs,
            "raw_bm25_docs": all_bm25_docs,
            "deduplicated_docs": all_combined_docs,
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