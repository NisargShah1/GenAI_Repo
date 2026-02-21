import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

# Static mapping of sectors to top Indian stocks (NSE) for demo purposes
SECTOR_MAPPING = {
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "AUTO": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "PHARMA": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
    "FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "ENERGY": ["RELIANCE.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS"],
    "METAL": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS"]
}

class MarketDataTool:
    def get_stocks_by_sector(self, sector_name):
        """Returns a list of top stock tickers for a given sector."""
        sector_key = sector_name.upper()
        # Simple fuzzy matching or direct lookup
        for key in SECTOR_MAPPING:
            if key in sector_key or sector_key in key:
                return SECTOR_MAPPING[key]
        return []

    def get_stock_price_data(self, ticker, period="1y"):
        """Fetches historical price data and calculates technical indicators."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return None

            # Calculate Indicators
            # Simple Moving Averages
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            
            # RSI (Relative Strength Index)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # MACD
            macd = ta.macd(df['Close'])
            df = pd.concat([df, macd], axis=1)

            # Get the latest data point
            latest = df.iloc[-1].to_dict()
            latest['Current_Price'] = latest['Close']
            latest['Date'] = df.index[-1].strftime('%Y-%m-%d')
            
            # Add some context (Trend)
            latest['Trend_50_SMA'] = "Bullish" if latest['Close'] > latest['SMA_50'] else "Bearish"
            latest['Trend_200_SMA'] = "Bullish" if latest['Close'] > latest['SMA_200'] else "Bearish"
            
            return latest
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def get_stock_news(self, ticker):
        """Fetches recent news for a specific stock."""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            simplified_news = []
            if news:
                for item in news[:5]: # Top 5 news items
                    simplified_news.append({
                        "title": item.get('title'),
                        "publisher": item.get('publisher'),
                        "link": item.get('link'),
                        "relatedTickers": item.get('relatedTickers')
                    })
            return simplified_news
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    def get_company_info(self, ticker):
        """Fetches basic company info."""
        try:
            stock = yf.Ticker(ticker)
            return {
                "sector": stock.info.get('sector'),
                "industry": stock.info.get('industry'),
                "marketCap": stock.info.get('marketCap'),
                "forwardPE": stock.info.get('forwardPE'),
                "trailingPE": stock.info.get('trailingPE'),
                "beta": stock.info.get('beta')
            }
        except Exception:
            return {}
