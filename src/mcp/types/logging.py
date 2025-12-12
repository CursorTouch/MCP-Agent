from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Literal
from src.mcp.types.common import LoggingLevel, RequestId

class SetLevelRequestParams(BaseModel):
    level: LoggingLevel
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class SetLevelRequest(BaseModel):
    method: Literal["logging/setLevel"] = "logging/setLevel"
    params: SetLevelRequestParams
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')

class LoggingMessageNotificationParams(BaseModel):
    level: LoggingLevel
    logger: Optional[str] = None
    data: Any
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class LoggingMessageNotification(BaseModel):
    method: Literal["notifications/message"] = "notifications/message"
    params: LoggingMessageNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')
