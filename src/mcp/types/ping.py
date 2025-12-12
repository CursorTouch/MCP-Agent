from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from src.mcp.types.common import RequestId, RequestParams

class PingRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["ping"] = "ping"
    params: Optional[RequestParams] = None
    
    model_config = ConfigDict(extra='allow')
