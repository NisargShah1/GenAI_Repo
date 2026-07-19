# GenAI Repository

This repository contains a collection of Generative AI projects exploring Agents, Model Context Protocol (MCP), RAG, and multi-agent workflows using Google Gemini and other LLMs.

## 📂 Projects Overview

| Project | Description | Tech Stack |
| :--- | :--- | :--- |
| **[Indian Stock Market Analysis](Indian_Stock_Market_Analysis/)** | Multi-agent AI system for analyzing Indian stocks (Technical, Fundamental, Sentiment) using Gemini. | Python, Google GenAI, yfinance, Rich CLI |
| **[Agentic-ReAct-java-spring](Agentic-ReAct-java-spring/)** | Java Spring Boot implementation of the ReAct pattern with Gemini, featuring streaming tool calls. | Java, Spring Boot, Google GenAI |
| **[Spring AI MCP Server](Spring_Ai_MCP_Server/)** | MCP Server built with Spring AI exposing tools like Weather and Email via SSE. | Java 21, Spring AI, Spring Boot |
| **[Agentic ReAct MCP Client](Agentic_ReAct_MCP_Client/)** | Python client using LangChain & LangGraph to orchestrate multi-step workflows with MCP tools. | Python, LangChain, LangGraph, MCP |
| **[Chat App (Mongo + Gemini)](chat-app/)** | Full-stack chat application to query MongoDB using natural language, rendering results as text, tables, or charts. | Spring Boot, React, MongoDB, Vertex AI |
| **[GenAI Test Impact Analysis](genai-test-impact-analysis/)** | Spring Boot PoC that analyzes Git diffs to identify impacted tests and suggests new test coverage using Gemini. | Java, Spring Boot, Google GenAI SDK |
| **[DocLoader (OCR)](docloader/)** | OCR utility for extracting text from printed (Tesseract) and handwritten (TrOCR) documents. | Python, Tesseract, TrOCR, Transformers |
| **[MCP Server (Python)](mcp_server/)** | Lightweight Python FastAPI server exposing basic MCP tools (e.g., Calculator). | Python, FastAPI, MCP |
| **[MCP Server with AI Agent](mcp_server_with_AI_Agent/)** | Python FastAPI server integrated with LangGraph for agentic workflows (e.g., Jokes, Calculator). | Python, FastAPI, LangGraph |
| **[Doc_RAG_System](Doc_RAG_System/)** | RAG system for querying scientific papers (PDFs) with hybrid retrieval and reranking. | Python, Streamlit, LangChain, FAISS, Gemini Pro |
| **[SDLC Skills Multi-Agent System](sdlc-skills-multi-agent-system/)** | Multi-agent system that runs a full SDLC sprint (requirement→design→code→test→review→docs) with **skills loaded on demand** to shrink prompts, cut tokens, and lower latency; tracks per-task token/latency telemetry. | Python, Google ADK, Gemini 2.5, Streamlit, SQLite |

## 🚀 Getting Started

Each project has its own `README.md` with specific setup and usage instructions. Please navigate to the respective project folder to get started.

## 🔑 Prerequisites

Most projects require:
- **API Keys**: Google Gemini API Key (or OpenAI/Vertex AI credentials).
- **Runtimes**:
  - Python 3.10+ (for Python projects)
  - Java 17/21+ (for Spring Boot projects)
- **Dependency Managers**:
  - `pip` (Python)
  - `maven` (Java)

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for new agents, tools, or improvements!
