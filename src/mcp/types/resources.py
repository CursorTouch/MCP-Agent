from pydantic import BaseModel,Field,ConfigDict
from typing import Optional

class Resource(BaseModel):
    uri: str
    name: str
    description: Optional[str]=None
    mimeType: Optional[str]=None
    size: Optional[int]=None

    model_config = ConfigDict(extra="allow")

class ResourceTemplate(BaseModel):
    uriTemplate: str
    name: str
    description: Optional[str]=None
    mimeType: Optional[str]=None

    model_config = ConfigDict(extra="allow")

class TextContent(BaseModel):
    uri: str
    name: Optional[str]=None
    title: Optional[str]=None
    mimeType: Optional[str]=None
    text: str

class BinaryContent(BaseModel):
    uri: str
    name: Optional[str]=None
    title: Optional[str]=None
    mimeType: Optional[str]=None
    blob: str

class ResourceResult(BaseModel):
    contents: list[TextContent | BinaryContent]

# Request Types
class ResourcesListRequest(BaseModel):
    cursor: Optional[str]=None
    model_config = ConfigDict(extra="allow")

class ResourcesReadRequest(BaseModel):
    uri: str
    model_config = ConfigDict(extra="allow")

class ResourcesTemplatesListRequest(BaseModel):
    cursor: Optional[str]=None
    model_config = ConfigDict(extra="allow")

class ResourcesSubscribeRequest(BaseModel):
    uri: str
    model_config = ConfigDict(extra="allow")

class ResourcesUnsubscribeRequest(BaseModel):
    uri: str
    model_config = ConfigDict(extra="allow")

# Result Types
class ResourcesListResult(BaseModel):
    resources: list[Resource]
    nextCursor: Optional[str]=None
    model_config = ConfigDict(extra="allow")

class ResourcesTemplatesListResult(BaseModel):
    resourceTemplates: list[ResourceTemplate]
    nextCursor: Optional[str]=None
    model_config = ConfigDict(extra="allow")