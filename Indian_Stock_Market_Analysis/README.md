# Indian Stock Market Analysis AI Agent 🇮🇳

An AI-powered multi-agent system designed to analyze Indian stocks (NSE/BSE). This tool leverages Google's Gemini models to provide comprehensive investment insights based on technical, fundamental, and sentiment analysis.

It offers two interfaces:
1.  **Interactive Web UI (Streamlit)**: Visual charts, expanding reports, and easy navigation.
2.  **Command Line Interface (CLI)**: Fast, text-based analysis for terminal users.

## 🚀 Features

- **Multi-Agent Architecture:**
  - **Technical Analyst:** Analyzes price action, moving averages (SMA 50/200), RSI, and MACD.
  - **Fundamental Analyst:** Evaluates key financial metrics (P/E, Market Cap, Beta) and sector positioning.
  - **Sentiment Analyst:** Scans recent news headlines to gauge market sentiment and identify potential catalysts.
  - **Portfolio Manager:** Synthesizes reports from all specialist agents to provide a final Buy/Sell/Hold recommendation.
- **Interactive UI:** Built with Streamlit for a rich user experience including Candlestick charts (Plotly).
- **Indian Market Focus:** Designed specifically for NSE tickers (e.g., `RELIANCE.NS`, `TCS.NS`).
- **Sector Analysis:** Can analyze top stocks within major sectors like Banking, IT, Auto, Pharma, FMCG, Energy, and Metal.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **AI Model:** Google Gemini Pro (`google-generativeai`)
- **Data Source:** `yfinance` (Yahoo Finance API)
- **Web UI:** `streamlit` + `plotly`
- **CLI:** `rich` library

---

## 📦 End-to-End Setup Guide

### 1. Prerequisites
- Python 3.10 or higher installed.
- A Google Gemini API Key. You can get one for free from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone the Repository
```bash
git clone https://github.com/NisargShah1/GenAI_Repo.git
cd GenAI_Repo/Indian_Stock_Market_Analysis
```

### 3. Create a Virtual Environment (Recommended)
It's best practice to run Python projects in an isolated environment.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory (`Indian_Stock_Market_Analysis/.env`) and add your API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

*(Alternatively, you can input the key directly in the Streamlit UI sidebar)*

---

## 🖥️ Usage

### Option A: Run the Web Application (Streamlit)
This is the recommended way to use the tool.

```bash
streamlit run streamlit_app.py
```

**How to use:**
1.  The app will open in your browser (usually `http://localhost:8501`).
2.  **Enter API Key:** If not set in `.env`, enter your Gemini API Key in the sidebar.
3.  **Select Mode:** Choose "Specific Ticker" or "Sector Analysis".
4.  **Input:** Enter a ticker (e.g., `TATAMOTORS`) or select a sector.
5.  Click **"Run Analysis"**.
6.  View the interactive price chart and read the detailed agent reports below.

### Option B: Run the CLI Tool
For quick analysis directly in your terminal.

```bash
python main.py
```

**How to use:**
1.  Run the script.
2.  Enter a ticker symbol (e.g., `INFY`) or a sector name (e.g., `IT`).
3.  The agents will run sequentially and print a formatted report to the console.

---

## 📂 Project Structure

```
Indian_Stock_Market_Analysis/
├── streamlit_app.py        # Streamlit Web Application Entry Point
├── main.py                 # CLI Entry Point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agents.py       # AI Agent definitions (Manager, Tech, Fund, Sent)
│   └── tools/
│       ├── __init__.py
│       └── market_data.py  # Data fetching (yfinance) and technical indicators
└── README.md
```

## ⚠️ Disclaimer

This tool is for **educational purposes only**. The AI-generated analysis may be inaccurate or hallucinated. Do not use it as the sole basis for real-world investment decisions. Always do your own research and consult a qualified financial advisor.
