import os
import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from dotenv import load_dotenv

from src.tools.market_data import MarketDataTool
from src.agents.agents import TechnicalAgent, FundamentalAgent, SentimentAgent, ManagerAgent

# Page Configuration
st.set_page_config(
    page_title="Indian Stock Market AI Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Environment Variables
load_dotenv()

# --- Custom Styling ---
st.markdown("""
<style>
    .report-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🔍 Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))

if not api_key:
    st.sidebar.warning("Please enter your Google Gemini API Key to proceed.")
    st.stop()

# --- Main App ---
st.title("🇮🇳 Indian Stock Market AI Analyst")
st.markdown("### Multi-Agent Analysis System powered by Gemini")

# Input Section
col1, col2 = st.columns([1, 2])

with col1:
    analysis_mode = st.radio("Analysis Mode:", ["Specific Ticker", "Sector Analysis"])

market_tool = MarketDataTool()
selected_ticker = ""

with col2:
    if analysis_mode == "Specific Ticker":
        ticker_input = st.text_input("Enter NSE Ticker (e.g., RELIANCE, TCS):", value="RELIANCE").upper()
        if ticker_input:
            selected_ticker = ticker_input if ticker_input.endswith(".NS") else f"{ticker_input}.NS"
    else:
        sector = st.selectbox("Select Sector:", ["BANKING", "IT", "AUTO", "PHARMA", "FMCG", "ENERGY", "METAL"])
        if sector:
            top_stocks = market_tool.get_stocks_by_sector(sector)
            selected_ticker = st.selectbox("Select Stock from Sector:", top_stocks)

if st.button("🚀 Run Analysis", type="primary"):
    if not selected_ticker:
        st.error("Please select a valid ticker.")
        st.stop()

    with st.status("🤖 AI Agents are working...", expanded=True) as status:
        
        # 1. Fetch Data
        st.write("📡 Fetching market data...")
        try:
            stock_data = market_tool.get_stock_price_data(selected_ticker, period="1y")
            company_info = market_tool.get_company_info(selected_ticker)
            news_data = market_tool.get_stock_news(selected_ticker)
            
            if not stock_data:
                status.update(label="Failed to fetch data", state="error")
                st.error(f"Could not fetch data for {selected_ticker}. Please check the ticker symbol.")
                st.stop()
                
        except Exception as e:
            status.update(label="Error fetching data", state="error")
            st.error(f"Error: {str(e)}")
            st.stop()

        # 2. Initialize Agents
        tech_agent = TechnicalAgent(api_key=api_key)
        fund_agent = FundamentalAgent(api_key=api_key)
        sent_agent = SentimentAgent(api_key=api_key)
        manager_agent = ManagerAgent(api_key=api_key)

        # 3. Agent Analysis
        st.write("📈 Technical Agent is analyzing price action...")
        tech_report = tech_agent.analyze(selected_ticker, stock_data)

        st.write("🏢 Fundamental Agent is evaluating company metrics...")
        fund_report = fund_agent.analyze(selected_ticker, company_info)

        st.write("📰 Sentiment Agent is reading news...")
        sent_report = sent_agent.analyze(selected_ticker, news_data)

        # 4. Final Synthesis
        st.write("👨‍💼 Portfolio Manager is synthesizing the recommendation...")
        final_report = manager_agent.synthesize(selected_ticker, tech_report, fund_report, sent_report)
        
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    # --- Display Results ---
    
    # Stock Price Chart
    st.subheader(f"Price Chart: {selected_ticker}")
    
    hist_df = market_tool.get_historical_data(selected_ticker, period="1y")
    if hist_df is not None:
        fig = go.Figure(data=[go.Candlestick(x=hist_df.index,
                    open=hist_df['Open'],
                    high=hist_df['High'],
                    low=hist_df['Low'],
                    close=hist_df['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not fetch historical data for chart.")

    # Manager's Final Report
    st.markdown("---")
    st.subheader("📝 Manager's Recommendation")
    st.success(final_report)

    # Detailed Reports in Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Technical Analysis", "🏢 Fundamental Analysis", "📰 Sentiment Analysis"])
    
    with tab1:
        st.markdown(tech_report)
        st.caption(f"RSI: {stock_data.get('RSI', 'N/A'):.2f} | SMA50: {stock_data.get('SMA_50', 'N/A'):.2f}")
        
    with tab2:
        st.markdown(fund_report)
        st.caption(f"Market Cap: {company_info.get('marketCap', 'N/A')} | P/E: {company_info.get('trailingPE', 'N/A')}")
        
    with tab3:
        st.markdown(sent_report)
        st.markdown("### Recent Headlines")
        for news in news_data:
            st.markdown(f"- [{news['title']}]({news['link']}) _({news['publisher']})_")

