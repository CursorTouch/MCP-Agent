from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Literal, Union
from src.mcp.types.common import Annotations, Icon, NotificationParams, RequestId, PaginatedRequestParams, Result, RequestParams

class Resource(BaseModel):
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    icons: Optional[list[Icon]] = None
    mimeType: Optional[str] = None
    name: str
    size: Optional[int] = None
    title: Optional[str] = None
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class ResourceTemplate(BaseModel):
    annotations: Optional[Annotations] = None
    description: Optional[str] = None
    icons: Optional[list[Icon]] = None
    mimeType: Optional[str] = None
    name: str
    title: Optional[str] = None
    uriTemplate: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class TextResourceContents(BaseModel):
    uri: str
    mimeType: Optional[str] = None
    text: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class BlobResourceContents(BaseModel):
    uri: str
    mimeType: Optional[str] = None
    blob: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class ReadResourceResult(Result):
    contents: list[Union[TextResourceContents, BlobResourceContents]]
    model_config = ConfigDict(extra="allow")

# Requests and Params

class ListResourcesRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["resources/list"] = "resources/list"
    params: Optional[PaginatedRequestParams] = None
    model_config = ConfigDict(extra="allow")

class ListResourcesResult(Result):
    resources: list[Resource]
    nextCursor: Optional[str] = None
    model_config = ConfigDict(extra="allow")

class ReadResourceRequestParams(BaseModel):
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class ReadResourceRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["resources/read"] = "resources/read"
    params: ReadResourceRequestParams
    model_config = ConfigDict(extra="allow")

class SubscribeRequestParams(BaseModel):
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class SubscribeRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["resources/subscribe"] = "resources/subscribe"
    params: SubscribeRequestParams
    model_config = ConfigDict(extra="allow")

class UnsubscribeRequestParams(BaseModel):
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class UnsubscribeRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["resources/unsubscribe"] = "resources/unsubscribe"
    params: UnsubscribeRequestParams
    model_config = ConfigDict(extra="allow")

class ListResourceTemplatesRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["resources/templates/list"] = "resources/templates/list"
    params: Optional[PaginatedRequestParams] = None
    model_config = ConfigDict(extra="allow")

class ListResourceTemplatesResult(Result):
    resourceTemplates: list[ResourceTemplate]
    nextCursor: Optional[str] = None
    model_config = ConfigDict(extra="allow")

# Notifications

class ResourceListChangedNotification(BaseModel):
    method: Literal["notifications/resources/list_changed"] = "notifications/resources/list_changed"
    params: Optional[NotificationParams] = None
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra="allow")

class ResourceUpdatedNotificationParams(BaseModel):
    uri: str
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra="allow")

class ResourceUpdatedNotification(BaseModel):
    method: Literal["notifications/resources/updated"] = "notifications/resources/updated"
    params: ResourceUpdatedNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra="allow")