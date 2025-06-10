User → MCP API → Agent -> LLM (choose tools) → [Tools + LLM] → Response

Steps
1. You have activated your virtual environment (recommended):

python -m venv venv
source venv/bin/activate      # On Linux/macOS
venv\Scripts\activate         # On Windows
2. Install packages from requirements.txt 
pip install -r requirements.txt

3. Run the server using below command
uvicorn main:app --reload

4. After server start open URL in browser
 Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

http://127.0.0.1:8000/docs

5. I t will open swagger page, Try run "mcp/task" endpoint by passing json request

{
  "sessionId": "usr-11",
  "model": "gemini-2.0-flash",
  "input": "tell me some funny thing",
  "tools": [] # optional
}

response:
{
  "sessionId": "usr-11",
  "status": "success",
  "output": "Why did the developer go broke? Because he used up all his cache!",
  "source": "langgraph",
  "usedTools": [
    "joke"
  ]
}

It supports openAi and gemini models , so pass models accordingly in request. 
NOTE: Update your OPENAI and GEMINI API key in .env file before running.



 