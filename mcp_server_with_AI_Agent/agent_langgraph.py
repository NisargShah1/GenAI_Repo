from langgraph.graph import StateGraph, END
from tools.calculator import calculate_if_needed
from tools.jokes import get_joke
from typing import TypedDict
from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    input: str
    response: str
    tools: list[str]
    model: str

def decide_tool(state: AgentState):
    input_text = state["input"]
    model_name = state.get("model", "gemini-2.0-flash")
    
    result = call_llm(input_text, model_name)
    print (f" LLM output is: {result}")
    if result in ["calculator", "joke"]:
        return result
    return END

def router(state: AgentState):
    return decide_tool(state)  # returns either 'calculator' or 'joke'


def call_llm(prompt, model="gpt-4"):
    if model.startswith("gpt"):
        # Use OpenAI
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
            {"role": "system", "content": "You are a helpful assistant that decides which tool to call: 'calculator' or 'joke'."},
            {"role": "user", "content": f"Decide the tool to use for: {prompt}. Return only 'calculator' or 'joke'."}
        ]
        )
        return response.choices[0].message.content.strip().lower()
    else:
        # Use Gemini
        gemini_model = genai.GenerativeModel(model)
        chat = gemini_model.start_chat(history=[])
        result = chat.send_message(
            f"Decide which tool to use for the following input. Only respond with 'calculator' or 'joke': {prompt}"
        ).text.strip().lower()
        return result

def call_calculator(state: AgentState):
    result = calculate_if_needed(state["input"], state["model"])
    print(f"calculator tool response: {result}")
    return {"response": result, "tools": ["calculator"]}

def call_joke(state: AgentState):
    result = get_joke()
    return {"response": result, "tools": ["joke"]}

def router(state: AgentState):
    return state  # Just pass state to the conditional edge logic

builder = StateGraph(AgentState)
builder.add_node("router", router)
builder.add_node("calculator", call_calculator)
builder.add_node("joke", call_joke)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    decide_tool,
    {
        "calculator": "calculator",
        "joke": "joke"
    }
)

builder.add_edge("calculator", END)
builder.add_edge("joke", END)

graph = builder.compile()