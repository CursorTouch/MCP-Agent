from typing import Optional, Literal, Any, Protocol, Union
from pydantic import BaseModel, ConfigDict, Field
from src.mcp.types.common import Error, RequestId, Result

from src.mcp.types.schemas import PrimitiveSchemaDefinition

class TaskMetadata(BaseModel):
    """
    Metadata about the task that is being performed.
    """
    ttl: Optional[float] = None
    model_config = ConfigDict(extra='allow')

class RequestedSchema(BaseModel):
    properties: dict[str, PrimitiveSchemaDefinition]
    required: Optional[list[str]] = None
    type: Literal["object"] = "object"
    
    model_config = ConfigDict(extra='allow')

class ElicitRequestFormParams(BaseModel):
    message: str
    mode: Literal["form"] = "form"
    requestedSchema: RequestedSchema
    task: Optional[TaskMetadata] = None
    
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class ElicitRequestURLParams(BaseModel):
    elicitationId: str
    message: str
    mode: Literal["url"] = "url"
    url: str
    task: Optional[TaskMetadata] = None
    
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

ElicitRequestParams = Union[ElicitRequestFormParams, ElicitRequestURLParams]

class ElicitRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["elicitation/create"] = "elicitation/create"
    params: ElicitRequestParams
    model_config = ConfigDict(extra='allow')

class ElicitResult(Result):
    action: Literal["accept", "decline", "cancel"]
    content: Optional[dict[str, Union[str, int, float, bool, list[str]]]] = None
    model_config = ConfigDict(extra='allow')

class ElicitationFn(Protocol):
    async def __call__(self, params: ElicitRequestParams) -> Union[ElicitResult, Error]:
        ...

class ElicitationCompleteNotificationParams(BaseModel):
    elicitationId: str
    model_config = ConfigDict(extra='allow')

class ElicitationCompleteNotification(BaseModel):
    method: Literal["notifications/elicitation/complete"] = "notifications/elicitation/complete"
    params: ElicitationCompleteNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')