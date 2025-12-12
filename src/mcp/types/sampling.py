from typing import Literal, Optional, Protocol, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from src.mcp.types.common import Error, Role, RequestId, ProgressToken, Result
from src.mcp.types.content import TextContent, ImageContent, AudioContent, ContentBlock
from src.mcp.types.tasks import TaskMetadata
from src.mcp.types.tools import Tool

StopReason = Literal["endTurn", "stopSequence", "maxTokens", "toolUse"]
IncludeContext = Literal["none", "thisServer", "allServers"]

class ModelHint(BaseModel):
    name: Optional[str] = None
    model_config = ConfigDict(extra='allow')

class ModelPreferences(BaseModel):
    costPriority: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    hints: Optional[list[ModelHint]] = None
    intelligencePriority: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    speedPriority: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    model_config = ConfigDict(extra='allow')

class ToolUseContent(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    input: dict[str, Any]
    name: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class ToolResultContent(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    content: list[ContentBlock]
    isError: bool = False
    structuredContent: Optional[dict[str, Any]] = None
    toolUseId: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

SamplingMessageContentBlock = Union[TextContent, ImageContent, ToolUseContent, ToolResultContent]

class SamplingMessage(BaseModel):
    content: Union[SamplingMessageContentBlock, list[SamplingMessageContentBlock]]
    role: Role
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class ToolChoice(BaseModel):
    mode: Literal["none", "required", "auto"] = "auto"
    model_config = ConfigDict(extra='allow')

class CreateMessageRequestParams(BaseModel):
    includeContext: Optional[IncludeContext] = "none"
    maxTokens: int
    messages: list[SamplingMessage]
    metadata: Optional[dict[str, Any]] = None
    modelPreferences: Optional[ModelPreferences] = None
    stopSequences: Optional[list[str]] = None
    systemPrompt: Optional[str] = None
    task: Optional[TaskMetadata] = None
    temperature: Optional[float] = None
    toolChoice: Optional[ToolChoice] = Field(default_factory=ToolChoice)
    tools: Optional[list[Tool]] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class CreateMessageRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["sampling/createMessage"] = "sampling/createMessage"
    params: CreateMessageRequestParams
    model_config = ConfigDict(extra='allow')

class CreateMessageResult(Result):
    content: Union[SamplingMessageContentBlock, list[SamplingMessageContentBlock]]
    model: str
    role: Role
    stopReason: Optional[Union[StopReason, str]] = None
    model_config = ConfigDict(extra='allow')

class SamplingFn(Protocol):
    async def __call__(self, params: CreateMessageRequestParams) -> Union[CreateMessageResult, Error]:
        ...