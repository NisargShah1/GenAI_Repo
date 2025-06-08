# orchestrator.py

from schemas import MCPRequest, MCPResponse
from tools.calculator import calculate_if_needed
from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def handle_request(req: MCPRequest) -> MCPResponse:
    output = ""
    used_tools = []

    if "calculator" in req.tools:
        result = calculate_if_needed(req.input)
        if result is not None:
            output = f"Calculated Result: {result}"
            used_tools.append("calculator")
        else:
            output = call_llm(req.input, model=req.model)
    else:
        output = call_llm(req.input, model=req.model)

    return MCPResponse(
        sessionId=req.sessionId,
        status="success",
        output=output,
        source=req.model,
        usedTools=used_tools
    )

def call_llm(prompt, model="gpt-4"):
    if model.startswith("gpt"):
        # Use OpenAI
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    else:
        # Use Gemini
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(prompt)
        return response.text