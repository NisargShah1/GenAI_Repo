import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.tools.market_data import MarketDataTool
from src.agents.agents import TechnicalAgent, FundamentalAgent, SentimentAgent, ManagerAgent, HedgingAgent

# Load environment variables
load_dotenv()

# Initialize Rich Console
console = Console()

def main():
    console.print(Panel.fit("[bold cyan]Indian Stock Market Analysis AI[/bold cyan]", subtitle="Multi-Agent System"))

    # Check for API Key
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY not found in environment variables.")
        console.print("Please set it in a .env file or your environment.")
        return

    # User Input
    ticker_input = console.input("[bold green]Enter Stock Ticker (e.g., RELIANCE, TCS) or Sector (e.g., BANKING): [/bold green]").strip().upper()
    
    if not ticker_input:
        console.print("[red]Input cannot be empty.[/red]")
        return

    # Initialize Tools
    market_tool = MarketDataTool()

    # Determine if input is a sector or ticker
    target_stocks = []
    if ticker_input in ["BANKING", "IT", "AUTO", "PHARMA", "FMCG", "ENERGY", "METAL"]:
        console.print(f"[yellow]Searching for top stocks in {ticker_input} sector...[/yellow]")
        target_stocks = market_tool.get_stocks_by_sector(ticker_input)
        if not target_stocks:
            console.print(f"[red]No stocks found for sector {ticker_input}.[/red]")
            return
        # For demo, pick the first one or ask user to select. Let's analyze the top one.
        console.print(f"Found: {', '.join(target_stocks)}")
        ticker_input = target_stocks[0] # Analyze the leader
        console.print(f"[bold]Analyzing Sector Leader: {ticker_input}[/bold]")
    else:
        # Assume it's a ticker, append .NS if missing
        if not ticker_input.endswith(".NS") and not ticker_input.endswith(".BO"):
             ticker_input += ".NS"
        target_stocks = [ticker_input]

    ticker = target_stocks[0]

    # Initialize Agents
    try:
        tech_agent = TechnicalAgent()
        fund_agent = FundamentalAgent()
        sent_agent = SentimentAgent()
        hedge_agent = HedgingAgent()
        manager_agent = ManagerAgent()
    except Exception as e:
        console.print(f"[red]Failed to initialize AI Agents: {e}[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        
        # Step 1: Data Gathering
        task1 = progress.add_task(f"[cyan]Fetching market data for {ticker}...[/cyan]", total=None)
        stock_data = market_tool.get_stock_price_data(ticker)
        company_info = market_tool.get_company_info(ticker)
        news_data = market_tool.get_stock_news(ticker)
        progress.update(task1, completed=True)

        if not stock_data:
            console.print(f"[red]Failed to fetch sufficient data for {ticker}. Check ticker symbol or data availability.[/red]")
            return

        # Step 2: Agent Analysis
        task2 = progress.add_task("[magenta]Running Technical Analysis...[/magenta]", total=None)
        tech_report = tech_agent.analyze(ticker, stock_data)
        progress.update(task2, completed=True)

        task3 = progress.add_task("[blue]Running Fundamental Analysis...[/blue]", total=None)
        fund_report = fund_agent.analyze(ticker, company_info)
        progress.update(task3, completed=True)

        task4 = progress.add_task("[yellow]Running Sentiment Analysis...[/yellow]", total=None)
        sent_report = sent_agent.analyze(ticker, news_data)
        progress.update(task4, completed=True)

        task5 = progress.add_task("[white]Running Hedging Analysis...[/white]", total=None)
        # Combine data for hedging
        combined_data = {**stock_data, 'beta': company_info.get('beta', 'N/A')}
        hedge_report = hedge_agent.analyze(ticker, tech_report, fund_report, sent_report, combined_data)
        progress.update(task5, completed=True)

        # Step 3: Synthesis
        task6 = progress.add_task("[green]Synthesizing Final Report...[/green]", total=None)
        final_report = manager_agent.synthesize(ticker, tech_report, fund_report, sent_report, hedge_report)
        progress.update(task6, completed=True)

    # Output Results
    console.print("\n")
    console.rule(f"[bold]Analysis Report for {ticker}[/bold]")
    
    console.print(Panel(Markdown(final_report), title="Manager's Recommendation", border_style="green"))
    
    console.print("\n[dim]Detailed Agent Reports:[/dim]")
    console.print(Panel(Markdown(tech_report), title="Technical Analysis", border_style="magenta"))
    console.print(Panel(Markdown(fund_report), title="Fundamental Analysis", border_style="blue"))
    console.print(Panel(Markdown(sent_report), title="Sentiment Analysis", border_style="yellow"))
    console.print(Panel(Markdown(hedge_report), title="Hedging Strategy", border_style="white"))

if __name__ == "__main__":
    main()
