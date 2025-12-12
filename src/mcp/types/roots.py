from typing import Optional, Protocol, Union, Literal, Any
from pydantic import BaseModel, ConfigDict, Field
from src.mcp.types.common import Error, NotificationParams, RequestId, Result, RequestParams

class Root(BaseModel):
    name: Optional[str] = None
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class ListRootsRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["roots/list"] = "roots/list"
    params: Optional[RequestParams] = None
    model_config = ConfigDict(extra='allow')

class ListRootsResult(Result):
    roots: list[Root]
    model_config = ConfigDict(extra='allow')

class RootsListChangedNotification(BaseModel):
    method: Literal["notifications/roots/list_changed"] = "notifications/roots/list_changed"
    params: Optional[NotificationParams] = None
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')

class ListRootsFn(Protocol):
    def __call__(self, params: Optional[RequestParams] = None) -> Union[ListRootsResult, Error]:
        ...