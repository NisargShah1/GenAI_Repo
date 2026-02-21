import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.agents.agents import LeadAIEngineerAgent

# Load environment variables
load_dotenv()

console = Console()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    console.print(Panel.fit("[bold cyan]Lead AI Engineer Code Review[/bold cyan]", subtitle="Automated Code Audit"))

    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY not found.")
        return

    files_to_review = [
        "src/tools/market_data.py",
        "main.py"
    ]

    engineer = LeadAIEngineerAgent()

    for file_path in files_to_review:
        console.rule(f"[bold]Reviewing: {file_path}[/bold]")
        
        try:
            code_content = read_file(file_path)
            result = engineer.review_and_instruct(file_path, code_content)
            
            status_color = "green" if result["status"] == "APPROVED" else "red"
            console.print(f"Status: [{status_color}]{result['status']}[/{status_color}]")
            
            console.print(Panel(Markdown(result["review"]), title="Lead Engineer's Feedback", border_style="yellow"))
            
            if result["status"] == "NEEDS_FIX":
                console.print(Panel(Markdown(result["fix_response"]), title="Proposed Fixes & Tests (from Code Fixer Agent)", border_style="blue"))
                
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")

if __name__ == "__main__":
    main()
