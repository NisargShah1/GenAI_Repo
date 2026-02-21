import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, model_name="gemini-pro"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
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

class CodeFixerAgent(BaseAgent):
    def fix_code(self, code_snippet, review_feedback):
        prompt = f"""
        You are a Senior Python Developer tasked with fixing code based on a code review.
        
        --- Original Code ---
        {code_snippet}
        
        --- Review Feedback ---
        {review_feedback}
        
        Task:
        1. Refactor the code to address all issues in the feedback.
        2. Ensure adherence to PEP 8 standards.
        3. Add type hints and docstrings if missing.
        4. Provide the COMPLETE corrected code block.
        5. Also generate a simple unit test using `unittest` or `pytest` to verify the fix.
        
        Output Format:
        [FIXED_CODE]
        ... code here ...
        [/FIXED_CODE]
        
        [TESTS]
        ... test code here ...
        [/TESTS]
        """
        return self.generate(prompt)

class LeadAIEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.fixer = CodeFixerAgent()

    def review_and_instruct(self, file_path, code_content):
        # Step 1: Review
        review_prompt = f"""
        You are a Lead AI Engineer reviewing Python code for a mission-critical financial application.
        Review the following code from `{file_path}`:

        {code_content}

        Criteria:
        1. **Code Quality**: PEP 8 compliance, variable naming, readability.
        2. **Security**: No hardcoded secrets, safe API usage.
        3. **Robustness**: Error handling (try-except blocks), edge case coverage.
        4. **Performance**: Efficient data structures and algorithms.
        5. **Documentation**: Presence of docstrings and type hints.

        If the code is perfect, respond with "APPROVED".
        If issues are found, list them clearly as bullet points under "ISSUES FOUND".
        """
        review_result = self.generate(review_prompt)

        if "APPROVED" in review_result:
            return {
                "status": "APPROVED",
                "review": review_result,
                "fixed_code": None,
                "tests": None
            }
        else:
            # Step 2: Instruct Fixer Agent
            fix_result = self.fixer.fix_code(code_content, review_result)
            return {
                "status": "NEEDS_FIX",
                "review": review_result,
                "fix_response": fix_result
            }
