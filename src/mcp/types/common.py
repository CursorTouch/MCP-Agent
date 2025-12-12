from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal, Union, Any

# Common Types
class Annotations(BaseModel):
    audience: Optional[list[Literal['user', 'assistant']]] = None
    lastModified: Optional[str] = None
    priority: Optional[float] = None
    
    model_config = ConfigDict(extra='allow')

class Icon(BaseModel):
    mimeType: Optional[str] = None
    sizes: Optional[list[str]] = None
    src: str
    theme: Optional[Literal["light", "dark"]] = None
    model_config = ConfigDict(extra='allow')

Cursor = str
ProgressToken = Union[str, int]
RequestId = Union[str, int]
Role = Literal["user", "assistant"]

class Result(BaseModel):
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

EmptyResult = Result

class NotificationParams(BaseModel):
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class RequestParams(BaseModel):
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class PaginatedRequestParams(RequestParams):
    cursor: Optional[str] = None
    model_config = ConfigDict(extra='allow')

class Error(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

    model_config = ConfigDict(extra='allow')

# LoggingLevel
LoggingLevel = Literal[
    "debug",
    "info",
    "notice",
    "warning",
    "error",
    "critical",
    "alert",
    "emergency"
]
