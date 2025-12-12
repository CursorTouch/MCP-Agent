from typing import Literal, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from src.mcp.types.common import Annotations, Role, Icon
from src.mcp.types.resources import TextResourceContents, BlobResourceContents

class TextContent(BaseModel):
    type: Literal['text'] = 'text'
    text: str
    annotations: Optional[Annotations] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class ImageContent(BaseModel):
    type: Literal['image'] = 'image'
    data: str
    mimeType: str
    annotations: Optional[Annotations] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class AudioContent(BaseModel):
    type: Literal['audio'] = 'audio'
    data: str
    mimeType: str
    annotations: Optional[Annotations] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class ResourceLink(BaseModel):
    type: Literal['resource_link'] = 'resource_link'
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None
    annotations: Optional[Annotations] = None
    icons: Optional[list[Icon]] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class EmbeddedResource(BaseModel):
    type: Literal['resource'] = 'resource'
    resource: Union[TextResourceContents, BlobResourceContents]
    annotations: Optional[Annotations] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

ContentBlock = Union[TextContent, ImageContent, AudioContent, ResourceLink, EmbeddedResource]
