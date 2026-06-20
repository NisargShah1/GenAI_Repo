# Doc_RAG_System

This project implements a RAG (Retrieval-Augmented Generation) system for querying scientific papers (PDFs).

## Features
- PDF Ingestion & Chunking
- Hybrid Retrieval (Semantic + Keyword)
- Reranking
- LLM Integration (Gemini Pro)
- Streamlit UI

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Add `.env` file with `GOOGLE_API_KEY`.
3. Place PDFs in `data/`.
4. Run ingestion: `python src/ingest.py`
5. Run app: `streamlit run app.py`
