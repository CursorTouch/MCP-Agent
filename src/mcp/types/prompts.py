from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Literal
from src.mcp.types.common import Role, Icon, NotificationParams, RequestId, PaginatedRequestParams, Result
from src.mcp.types.content import ContentBlock

class PromptArgument(BaseModel):
    description: Optional[str] = None
    name: str
    required: bool = False
    title: Optional[str] = None
    model_config = ConfigDict(extra='allow')

class Prompt(BaseModel):
    arguments: Optional[list[PromptArgument]] = None
    description: Optional[str] = None
    icons: Optional[list[Icon]] = None
    name: str
    title: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class PromptMessage(BaseModel):
    role: Role
    content: ContentBlock
    model_config = ConfigDict(extra='allow')

class GetPromptRequestParams(BaseModel):
    name: str
    arguments: Optional[dict[str, str]] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class GetPromptRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["prompts/get"] = "prompts/get"
    params: GetPromptRequestParams
    model_config = ConfigDict(extra='allow')

class GetPromptResult(Result):
    description: Optional[str] = None
    messages: list[PromptMessage]
    model_config = ConfigDict(extra='allow')

class ListPromptsRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["prompts/list"] = "prompts/list"
    params: Optional[PaginatedRequestParams] = None
    model_config = ConfigDict(extra='allow')

class ListPromptsResult(Result):
    prompts: list[Prompt]
    nextCursor: Optional[str] = None
    model_config = ConfigDict(extra='allow')

class PromptListChangedNotification(BaseModel):
    method: Literal["notifications/prompts/list_changed"] = "notifications/prompts/list_changed"
    params: Optional[NotificationParams] = None
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')