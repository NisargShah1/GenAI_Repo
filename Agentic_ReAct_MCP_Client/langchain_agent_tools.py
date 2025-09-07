import asyncio
import json
import os

import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Optional, final
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.session_context = None
        self.stream_context = None

    async def connect_to_sse_server(self, server_url: str, headers: Optional[dict]=None):
        self.stream_context = sse_client(url=server_url, headers = headers or {},)
        read_stream, write_stream = await self.stream_context.__aenter__()
        self.session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self.session_context.__aenter__()

        await self.session.initialize()

    async def get_tools(self):
        tools = await self.session.list_tools()
        print("Available tools:", tools)
        return tools

    def call_tool(self, name: str, args: dict):
        return asyncio.run(self.session.call_tool(name, args))

    async def cleanup(self):
        if self.session_context:
            await self.session_context.__aexit__(None,None,None)
        if self.stream_context:
            await self.stream_context.__aexit__(None, None, None)

class MCPToolWrapper:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client

    def make_tool(self, tool_info):
        """Convert MCP tool into LangChain Tool"""
        name = tool_info.name
        desc = tool_info.description

        print("Tool info:", tool_info)
        def _call(input: str|dict):
            # LangChain passes args as JSON string → convert
            if isinstance(input, str):
                args = json.loads(input)
            else:
                args = input
            return self.client.call_tool(name, args)

        return Tool(name=name, func=_call, description=desc)

async def build_mcp_agent(mcp: MCPClient, google_api_key: str):

    response = await mcp.get_tools()
    print("response", response)
    # Wrap tools
    tool_infos =  response.tools
    mcp_tools = [MCPToolWrapper(mcp).make_tool(t) for t in tool_infos]

    # Gemini LLM wrapper
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key
                                 ,system_instruction="You are a helpful assistant. Always use the MCP tool if available and call tools with arguments in json format only according to input parameters provided in tools description.")

    # LangChain Agent
    agent = initialize_agent(
        tools=mcp_tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    return agent

async def main():
    mcp = MCPClient()
    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        MCP_URL = "http://localhost:8080/mcp/sse"  # replace with your MCP server URL

        await mcp.connect_to_sse_server(MCP_URL, "")
        agent = await build_mcp_agent(mcp, GOOGLE_API_KEY)
        result = agent.run("What is the weather in Pune? and send weather details to nisarg.shah84@gmail.com. Use tools if available and call tools with arguments in json format only according to input parameters provided in tools description.")
        print(result)

        result = agent.run(
            "What is the capital of India? and send answer to nisarg.shah84@gmail.com.")
        print(result)

    finally:
        await mcp.cleanup()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
