from schemas import MCPRequest, MCPResponse
from langgraph_runner import run_graph

async def handle_request(req: MCPRequest) -> MCPResponse:
    output, tools_used = await run_graph(req.input, req.model)
    return MCPResponse(
        sessionId=req.sessionId,
        status="success",
        output=output,
        source="langgraph",
        usedTools=tools_used
    )