import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, api_key=None, model_name="gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables or passed as argument.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
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
        Suggest a stop-loss strategy based on volatility or recent lows (implied).
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
        Compare these metrics to typical Indian sector averages mentally.
        Assess the company's stability based on market cap and beta.
        """
        return self.generate(prompt)

class SentimentAgent(BaseAgent):
    def analyze(self, ticker, news_list):
        news_text = "\n".join([f"- {n['title']} (Source: {n['publisher']})" for n in news_list])
        prompt = f"""
        You are a Market Sentiment Analyst.
        Analyze the following recent news headlines for {ticker}:

        {news_text}

        Determine the overall sentiment (Positive/Negative/Neutral).
        Highlight any major risks or catalysts mentioned in the news.
        Ignore irrelevant or generic market news; focus on the specific company.
        """
        return self.generate(prompt)

class ManagerAgent(BaseAgent):
    def synthesize(self, ticker, technical_analysis, fundamental_analysis, sentiment_analysis):
        prompt = f"""
        You are a Portfolio Manager for the Indian Stock Market.
        Synthesize the following reports for {ticker} into a final investment recommendation.

        --- Technical Analysis ---
        {technical_analysis}

        --- Fundamental Analysis ---
        {fundamental_analysis}

        --- Sentiment Analysis ---
        {sentiment_analysis}

        Generate a structured report:
        1. **Executive Summary**: Buy, Sell, or Hold?
        2. **Key Drivers**: What are the main factors (technical, fundamental, news)?
        3. **Risk Assessment**: What should the investor watch out for?
        4. **Target Strategy**: Short-term vs Long-term perspective.
        
        Keep it professional, concise, and actionable for an Indian retail investor.
        """
        return self.generate(prompt)
