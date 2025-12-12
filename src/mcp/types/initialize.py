from src.mcp.types.capabilities import ClientCapabilities,ServerCapabilities
from src.mcp.types.info import Implementation
from src.mcp.types.common import RequestId
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Literal

class InitializeRequestParams(BaseModel):
    protocolVersion: str
    capabilities: ClientCapabilities
    clientInfo: Implementation
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    
    model_config = ConfigDict(extra='allow')

class InitializeRequest(BaseModel):
    method: Literal["initialize"] = "initialize"
    params: InitializeRequestParams
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    
    model_config = ConfigDict(extra='allow')

class InitializeResult(BaseModel):
    protocolVersion: str
    capabilities: ServerCapabilities
    serverInfo: Implementation
    instructions: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')