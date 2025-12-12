from typing import Optional, Any, Literal, Union
from pydantic import BaseModel, ConfigDict, Field
from src.mcp.types.common import Icon, NotificationParams, RequestId, PaginatedRequestParams, Result
from src.mcp.types.content import ContentBlock
from src.mcp.types.tasks import TaskMetadata

class ToolAnnotations(BaseModel):
    destructiveHint: bool = True
    idempotentHint: bool = False
    openWorldHint: bool = True
    readOnlyHint: bool = False
    title: Optional[str] = None
    model_config = ConfigDict(extra="allow")

class ToolExecution(BaseModel):
    taskSupport: Literal["forbidden", "optional", "required"] = "forbidden"
    model_config = ConfigDict(extra="allow")

class Tool(BaseModel):
    annotations: Optional[ToolAnnotations] = None
    description: Optional[str] = None
    execution: Optional[ToolExecution] = None
    icons: Optional[list[Icon]] = None
    inputSchema: dict[str, Any]
    name: str
    outputSchema: Optional[dict[str, Any]] = None
    title: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class CallToolRequestParams(BaseModel):
    arguments: Optional[dict[str, Any]] = None
    name: str
    task: Optional[TaskMetadata] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class CallToolRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tools/call"] = "tools/call"
    params: CallToolRequestParams
    model_config = ConfigDict(extra="allow")

class CallToolResult(Result):
    content: list[ContentBlock]
    isError: Optional[bool] = False
    structuredContent: Optional[dict[str, Any]] = None
    model_config = ConfigDict(extra="allow")

class ListToolsRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tools/list"] = "tools/list"
    params: Optional[PaginatedRequestParams] = None
    model_config = ConfigDict(extra="allow")

class ListToolsResult(Result):
    tools: list[Tool]
    nextCursor: Optional[str] = None
    model_config = ConfigDict(extra="allow")

class ToolListChangedNotification(BaseModel):
    method: Literal["notifications/tools/list_changed"] = "notifications/tools/list_changed"
    params: Optional[NotificationParams] = None
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra="allow")
