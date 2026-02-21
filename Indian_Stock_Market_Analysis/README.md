# Indian Stock Market Analysis AI

An AI-powered multi-agent system for analyzing Indian stocks (NSE/BSE). This tool leverages Google's Gemini models to provide comprehensive investment insights based on technical, fundamental, and sentiment analysis.

## Features

- **Multi-Agent Architecture:**
  - **Technical Analyst:** Analyzes price action, moving averages (SMA 50/200), RSI, and MACD.
  - **Fundamental Analyst:** Evaluates key financial metrics (P/E, Market Cap, Beta) and sector positioning.
  - **Sentiment Analyst:** Scans recent news headlines to gauge market sentiment and identify potential catalysts.
  - **Lead AI Engineer:** Audits code quality and security, delegating fixes to the Code Fixer agent.
  - **Code Fixer Agent:** Receives feedback from the Lead Engineer and generates corrected code with unit tests.
- **Indian Market Focus:** Designed specifically for NSE tickers (e.g., `RELIANCE.NS`, `TCS.NS`).
- **Sector Analysis:** Can analyze top stocks within major sectors like Banking, IT, Auto, etc.
- **Rich CLI:** Interactive terminal interface with progress indicators and formatted reports.

## Tech Stack

- **Language:** Python 3.10+
- **AI Model:** Google Gemini Pro (`google-generativeai`)
- **Data Source:** `yfinance` (Yahoo Finance API)
- **Technical Indicators:** `pandas_ta`
- **UI:** `rich` library for terminal formatting

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/GenAI_Repo.git
    cd GenAI_Repo/Indian_Stock_Market_Analysis
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    - Create a `.env` file in the root directory.
    - Add your Google Gemini API key:
      ```env
      GOOGLE_API_KEY=your_api_key_here
      ```
    - You can get a key from [Google AI Studio](https://aistudio.google.com/).

## Usage

Run the main script:

```bash
python main.py
```

Run the Code Review Agent:

```bash
python review_code.py
```

### Modes:

1.  **Single Ticker:**
    - Enter a stock symbol (e.g., `RELIANCE`, `TCS`, `INFY`).
    - The system will automatically append `.NS` for NSE if omitted.

2.  **Sector Analysis:**
    - Enter a sector name (e.g., `BANKING`, `IT`, `AUTO`).
    - The system will pick a top stock from that sector (e.g., HDFCBANK for BANKING) and analyze it.

## Project Structure

```
Indian_Stock_Market_Analysis/
├── main.py                 # Entry point
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

## Disclaimer

This tool is for educational purposes only. Do not use it as the sole basis for real-world investment decisions. Always do your own research.
