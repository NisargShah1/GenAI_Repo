import asyncio
import json
import os
import re
from functools import partial

import nest_asyncio
from typing import Optional, TypedDict, Dict, Any

from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END


# ---------------- Schema ----------------
class AgentState(TypedDict, total=False):
    query: str
    history: str
    next_action: Dict[str, Any]


# ---------------- MCP Client ----------------
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.session_context = None
        self.stream_context = None

    async def connect_to_sse_server(self, server_url: str, headers: Optional[dict] = None):
        self.stream_context = sse_client(url=server_url, headers=headers or {})
        read_stream, write_stream = await self.stream_context.__aenter__()
        self.session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self.session_context.__aenter__()
        await self.session.initialize()

    async def get_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, name: str, args: dict):
        return await self.session.call_tool(name, args)

    async def cleanup(self):
        if self.session_context:
            await self.session_context.__aexit__(None, None, None)
        if self.stream_context:
            await self.stream_context.__aexit__(None, None, None)


# ---------------- LangGraph Functions ----------------

async def decide_next(state: AgentState, llm, available_tools):
    """
    Use Gemini to decide next tool call or finish
    """
    prompt = (
        f"Conversation so far:\n{state.get('history', '')}\n\n"
        f"User request: {state['query']}\n\n"
        f"Available tools: {', '.join([t.name for t in available_tools])}\n\n"
        "Rules:\n"
        "1. You may call multiple tools in sequence if needed.\n"
        "2. Do not call the same tool repeatedly unless new input is provided.\n"
        "3. When done, return a final answer.\n\n"
        "4. For tool arguments stick to the input parameters given in tool descriptions"
        "Return only valid JSON in one of these formats:\n"
        '{"tool_call": {"name": "<tool_name>", "args": {...}}}\n'
        'or {"final_answer": "..."}\n'
    )

    response = await llm.ainvoke(prompt)
    print("Prompt:", prompt)
    print("llm response:", response.content)
    try:
        cleaned = re.sub(r"^```json|```$", "", response.content.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(cleaned)
    except Exception as e:
        raise Exception(f"JSON parsing failed: {e}, raw={response.content}")

    return {"next_action": parsed}


async def call_mcp(state: AgentState, mcp: MCPClient):
    """
    Execute MCP tool call
    """
    tool_name = state["next_action"]["tool_call"]["name"]
    args = state["next_action"]["tool_call"]["args"]
    result = await mcp.session.call_tool(tool_name, args)

    result_text = result.content if hasattr(result, "content") else str(result)

    return {
        "history": state.get("history", "") + f"\nTool {tool_name}({args}) -> {result_text}",
        "last_tool_result": result_text
    }


# ---------------- Build Workflow ----------------
async def build_workflow(mcp: MCPClient, google_api_key: str):
    tools_response = await mcp.get_tools()
    available_tools = tools_response.tools

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=google_api_key,
        model_kwargs={
            "system_instruction":"You are a helpful assistant. Always use the MCP tool if available. "
            "Return JSON in the format: "
             f"Always return JSON: If tool call required then return in this format. Stick to the input parameters defined in tool description:"
        f'{{"tool_call": {{"name": "...", "args": {{...}}}}}} '
        f'or if tool call not required then this format:   {{"final_answer": "..."}}'

        }
    )

    graph = StateGraph(AgentState)

    graph.add_node("decide", partial(decide_next, llm=llm, available_tools=available_tools))
    graph.add_node("tool", partial(call_mcp, mcp=mcp))

    def route_decision(state: AgentState):
        if "tool_call" in state["next_action"]:
            return "tool"
        elif "final_answer" in state["next_action"]:
            return "final"
        return "final"

    graph.add_conditional_edges(
        "decide",
        route_decision,
        {"tool": "tool", "final": END}
    )

    graph.add_edge("tool", "decide")
    graph.set_entry_point("decide")

    return graph.compile()



# ---------------- Main ----------------
async def main():
    mcp = MCPClient()
    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        MCP_URL = "http://localhost:8080/mcp/sse"

        await mcp.connect_to_sse_server(MCP_URL, "")
        workflow = await build_workflow(mcp, GOOGLE_API_KEY)

        # Run query
        result = await workflow.ainvoke({"query": "What is the weather in Pune? Send email of weather details to nisarg.shah84@gmail.com", "history": ""})
        print("Final Result:", result)

        #result = await workflow.ainvoke({"query": "What is the capital of India?", "history": ""})
        #print("Final Result:", result)

    finally:
        await mcp.cleanup()


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
