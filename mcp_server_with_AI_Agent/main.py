from fastapi import FastAPI
from router import router

app = FastAPI(title="MCP Server")

app.include_router(router, prefix="/mcp")
