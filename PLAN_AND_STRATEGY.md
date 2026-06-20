# ArXiv RAG System - Strategy & Implementation Plan

## 1. Architectural Overview

We are building a production-grade RAG system to answer questions from scientific papers (ArXiv). The system features a robust ingestion pipeline, a hybrid retrieval engine, and an agentic generation layer, exposed via a Streamlit UI.

### System Components

1.  **Ingestion Layer:**
    *   **Loader:** `PyMuPDF` / `LangChain` loaders for precise PDF text extraction.
    *   **Chunking:** Recursive Character Text Splitter with overlap to maintain semantic context across breaks.
    *   **Embedding Models (Experimentation):**
        *   *Baseline:* `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`) for local speed/cost efficiency.
        *   *Commercial:* `GoogleGenerativeAIEmbeddings` (`models/embedding-001`) for higher semantic density.
    *   **Vector Store:** `ChromaDB` (persistent) for local vector storage and retrieval.

2.  **Retrieval Layer:**
    *   **Strategy:** Two-stage retrieval.
        *   *Stage 1:* Semantic Search (Top-K) via ChromaDB.
        *   *Stage 2:* Re-ranking (Cross-Encoder) to filter irrelevant results and improve precision.
    *   **Agentic Extension (Stretch Goal 3):** Implementation of "Corrective RAG" (CRAG). If retrieval relevance is low, the agent falls back to web search (Google Search / Tavily) to ground the answer.

3.  **Generation Layer:**
    *   **LLM:** Google Gemini Pro (via `langchain-google-genai`) for reasoning and answer synthesis.
    *   **Prompt Engineering:** Few-shot prompting with strict citation requirements (Source Document + Page Number).

4.  **Interface Layer (Stretch Goal 2):**
    *   **Framework:** `Streamlit`.
    *   **Features:** Chat interface, model selection (Open Source vs Commercial Embeddings), and "Source Inspector" to view retrieved chunks.

## 2. Implementation Steps

### Phase 1: Environment & Setup
*   Initialize Python environment.
*   Install dependencies: `langchain`, `chromadb`, `streamlit`, `google-generativeai`, `sentence-transformers`, `pypdf`, `faiss-cpu`.
*   Configure API Keys securely (`.env`).

### Phase 2: Data Ingestion Pipeline (`ingest.py`)
*   Script to load PDFs from a `/data` directory.
*   Implement chunking strategy (Chunk Size: 1000, Overlap: 200).
*   Generate embeddings and persist to ChromaDB.
*   *Outcome:* A queryable local vector database.

### Phase 3: RAG Core & Retrieval Logic (`rag_engine.py`)
*   Define `retrieve_documents(query)` function.
*   Implement switching logic between embedding models.
*   Integrate the LLM for answer generation.
*   *Outcome:* Python functions that take a query and return an answer + citations.

### Phase 4: Agentic Capabilities (`agent.py` - Stretch Goal 3)
*   Implement a relevance grader (LLM-based) to score retrieved documents.
*   If score < threshold -> Trigger Web Search.
*   Synthesize final answer from (Docs + Web).

### Phase 5: User Interface (`app.py` - Stretch Goal 2)
*   Build the Streamlit frontend.
*   Connect UI inputs to the RAG backend.
*   Display chat history and sources.

## 3. Best Practices & Design Decisions

*   **Modularity:** Ingestion, retrieval, and UI are decoupled. This allows swapping the vector store or LLM without breaking the frontend.
*   **Observability:** We will log retrieval scores to understand when the model is "guessing" vs. "knowing."
*   **Security:** API keys are never hardcoded.

## 4. Execution Plan
1.  Commit this Plan & Strategy.
2.  Set up project structure (`/src`, `/data`, `requirements.txt`).
3.  Execute Phase 1 (Ingestion).
4.  Execute Phase 3 & 4 (Core Logic).
5.  Execute Phase 5 (UI).
