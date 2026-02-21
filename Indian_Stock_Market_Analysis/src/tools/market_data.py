import yfinance as yf
import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Optional, Any

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
    def get_stocks_by_sector(self, sector_name: str) -> List[str]:
        """Returns a list of top stock tickers for a given sector."""
        sector_key = sector_name.upper()
        for key in SECTOR_MAPPING:
            if key in sector_key or sector_key in key:
                return SECTOR_MAPPING[key]
        return []

    def get_stock_price_data(self, ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Fetches historical price data and calculates technical indicators."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                print(f"No data found for {ticker}")
                return None

            # Calculate Indicators
            # Ensure we have enough data for 200 SMA
            if len(df) < 200:
                print(f"Insufficient data for {ticker} (need >200 days for SMA200)")
                return None

            # Simple Moving Averages
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            
            # RSI (Relative Strength Index)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # MACD
            macd = ta.macd(df['Close'])
            if macd is not None:
                df = pd.concat([df, macd], axis=1)

            # Get the latest data point
            latest = df.iloc[-1].to_dict()
            latest['Current_Price'] = latest['Close']
            latest['Date'] = df.index[-1].strftime('%Y-%m-%d')
            
            # Handle potential NaNs in calculations
            sma50 = latest.get('SMA_50')
            sma200 = latest.get('SMA_200')
            close_price = latest.get('Close')

            if pd.notna(sma50) and pd.notna(close_price):
                latest['Trend_50_SMA'] = "Bullish" if close_price > sma50 else "Bearish"
            else:
                latest['Trend_50_SMA'] = "Unknown"

            if pd.notna(sma200) and pd.notna(close_price):
                latest['Trend_200_SMA'] = "Bullish" if close_price > sma200 else "Bearish"
            else:
                latest['Trend_200_SMA'] = "Unknown"
            
            return latest
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def get_stock_news(self, ticker: str) -> List[Dict[str, Any]]:
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

    def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetches basic company info."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "marketCap": info.get('marketCap', 'N/A'),
                "forwardPE": info.get('forwardPE', 'N/A'),
                "trailingPE": info.get('trailingPE', 'N/A'),
                "beta": info.get('beta', 'N/A')
            }
        except Exception:
            return {}
