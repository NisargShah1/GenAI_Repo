from pydantic import BaseModel
from typing import List, Optional

class MCPRequest(BaseModel):
    sessionId: str
    model: Optional[str] = "gpt-4"
    input: str
    tools: Optional[List[str]] = []

class MCPResponse(BaseModel):
    sessionId: str
    status: str
    output: str
    source: str
    usedTools: Optional[List[str]] = []
