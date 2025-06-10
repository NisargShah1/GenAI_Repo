from fastapi import APIRouter
from schemas import MCPRequest, MCPResponse
from orchestrator import handle_request

router = APIRouter()

@router.post("/task", response_model=MCPResponse)
async def process_task(req: MCPRequest):
    return await handle_request(req)


@router.get("/test")
async def test():
    return {"message": "MCP Server is running. Visit /docs for API UI."}