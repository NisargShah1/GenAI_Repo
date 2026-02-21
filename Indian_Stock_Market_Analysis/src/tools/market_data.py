import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
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

    def get_historical_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetches raw historical OHLCV data."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return None

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates SMA, RSI, and MACD manually using pandas."""
        # SMA
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        k = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
        d = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
        df['MACD'] = k - d
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False, min_periods=9).mean()
        
        return df

    def get_stock_price_data(self, ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Fetches historical price data and calculates technical indicators."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                print(f"No data found for {ticker}")
                return None

            # Calculate Indicators
            if len(df) < 200:
                print(f"Insufficient data for {ticker} (need >200 days for SMA200)")
                # Continue but some indicators will be NaN
            
            df = self.calculate_indicators(df)

            # Get the latest data point
            latest = df.iloc[-1].to_dict()
            latest['Current_Price'] = latest['Close']
            latest['Date'] = df.index[-1].strftime('%Y-%m-%d')
            
            # Map manual MACD names to expected keys if needed or keep new ones
            latest['MACD_12_26_9'] = latest.get('MACD')
            latest['MACDs_12_26_9'] = latest.get('MACD_Signal')
            
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
        """Scrapes Google News for recent headlines about a specific stock."""
        try:
            # Clean ticker (remove .NS suffix for better search results)
            search_term = ticker.replace(".NS", "").replace(".BO", "") + " stock news India"
            url = f"https://www.google.com/search?q={search_term}&tbm=nws&gl=IN&hl=en-IN"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_results = []
            
            # Google News structure changes often, but usually articles are in div containers
            # Common structure for search results (tbm=nws)
            # Title is usually in h3 or similar heading tag within a div class=" SoaBEf" (may vary)
            
            # Attempt to find main news blocks
            # This selector targets the main container for news items in Google Search News tab
            articles = soup.select('div.SoaBEf') 
            
            if not articles:
                 # Fallback for mobile view or different layout sometimes served
                 articles = soup.select('div.Gx5Zad')

            for article in articles[:5]: # Top 5
                try:
                    title_elem = article.select_one('div[role="heading"]') or article.select_one('.n0jPhd') or article.select_one('h3')
                    link_elem = article.find('a')
                    source_elem = article.select_one('.MgUUmf span') or article.select_one('.NUnG9d span') or article.select_one('.CEMjEf span')
                    
                    if title_elem and link_elem:
                        news_results.append({
                            "title": title_elem.get_text(),
                            "link": link_elem['href'],
                            "publisher": source_elem.get_text() if source_elem else "Google News",
                            "relatedTickers": [] # Not easily available via scraping
                        })
                except Exception:
                    continue
            
            if not news_results:
                print(f"No news found via scraping for {ticker}, falling back to empty list.")
                
            return news_results

        except Exception as e:
            print(f"Error scraping news for {ticker}: {e}")
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
