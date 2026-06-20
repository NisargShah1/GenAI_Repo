from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found.")

        # NEW client style (modern SDK)
        self.client = genai.Client(api_key=self.api_key)
        self.model = None  # Not used in new client, but kept for compatibility if needed
        self.model_name = model_name

    def generate(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"


class TechnicalAgent(BaseAgent):
    def analyze(self, ticker, data):
        prompt = f"""
You are a Technical Analysis Expert for the Indian Stock Market.

Analyze the following technical indicators for {ticker}:

Current Price: {data.get('Current_Price')}
RSI (14): {data.get('RSI')}
SMA (50): {data.get('SMA_50')}
SMA (200): {data.get('SMA_200')}
MACD: {data.get('MACD_12_26_9')}
MACD Signal: {data.get('MACDs_12_26_9')}
Trend vs 50 SMA: {data.get('Trend_50_SMA')}
Trend vs 200 SMA: {data.get('Trend_200_SMA')}

Provide a concise technical outlook (Bullish/Bearish/Neutral).
Identify key support/resistance levels if inferable from the moving averages.
Suggest a stop-loss strategy based on volatility or recent lows.
"""
        return self.generate(prompt)


class FundamentalAgent(BaseAgent):
    def analyze(self, ticker, info):
        prompt = f"""
You are a Fundamental Analysis Expert for Indian Stocks.

Analyze the following fundamental data for {ticker}:

Sector: {info.get('sector')}
Industry: {info.get('industry')}
Market Cap: {info.get('marketCap')}
Forward P/E: {info.get('forwardPE')}
Trailing P/E: {info.get('trailingPE')}
Beta: {info.get('beta')}

Provide a fundamental outlook (Undervalued/Overvalued/Fair).
Compare these metrics to sector averages mentally.
Assess company stability based on market cap and beta.
"""
        return self.generate(prompt)


class SentimentAgent(BaseAgent):
    def analyze(self, ticker, news_list):
        news_text = "\n".join(
            [f"- {n['title']} (Source: {n['publisher']})" for n in news_list]
        )

        prompt = f"""
You are a Market Sentiment Analyst.

Analyze the following recent news headlines for {ticker}:

{news_text}

Determine overall sentiment (Positive/Negative/Neutral).
Highlight major risks or catalysts.
Ignore irrelevant generic market news.
"""
        return self.generate(prompt)


class HedgingAgent(BaseAgent):
    def analyze(self, ticker, technical_view, fundamental_view, sentiment_view, market_data):
        prompt = f"""
        You are a Risk Management and Hedging Expert for the Indian Stock Market.
        Based on the detailed analysis provided by other agents for {ticker}, suggest a robust hedging strategy.

        --- Technical Outlook ---
        {technical_view}

        --- Fundamental Outlook ---
        {fundamental_view}

        --- Sentiment Outlook ---
        {sentiment_view}

        --- Key Metrics ---
        Current Price: {market_data.get('Current_Price')}
        Beta: {market_data.get('beta', 'N/A')}

        Task:
        1. **Synthesize Risk**: Combine the technical trend (e.g., bearish reversal), fundamental stability (e.g., high valuation), and sentiment (e.g., negative news) to assess the *real* downside risk.
        2. **Suggest Hedging Strategy**: 
           - If the outlook is **Bullish but Volatile**: Suggest buying cheap OTM Puts or a trailing stop-loss.
           - If **Bearish**: Suggest selling Call Options (Covered Call) or buying Puts / Inverse ETFs.
           - If **Neutral/Stagnant**: Suggest Iron Condors or simply holding cash.
           - Consider instrument availability in India (Nifty Futures, Stock Options, Liquid Bees).
        3. **Allocation**: How much of the position should be hedged? (e.g., "Hedge 50% of exposure").
        
        Provide a "Risk Rating" (Low/Medium/High) and a concrete "Action Plan".
        """
        return self.generate(prompt)


class ManagerAgent(BaseAgent):
    def synthesize(self, ticker, technical_analysis, fundamental_analysis, sentiment_analysis, hedging_strategy):
        prompt = f"""
You are a Portfolio Manager for the Indian Stock Market.

Synthesize the following reports for {ticker}:

--- Technical ---
{technical_analysis}

--- Fundamental ---
{fundamental_analysis}

--- Sentiment ---
{sentiment_analysis}

--- Hedging Strategy ---
{hedging_strategy}

Generate structured report:

1. Executive Summary → Buy / Sell / Hold
2. Key Drivers
3. Risk & Hedging Strategy
4. Target Strategy (Short vs Long term)

Keep it professional and concise.
"""
        return self.generate(prompt)
