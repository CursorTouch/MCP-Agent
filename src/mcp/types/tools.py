from src.mcp.types.resources import TextContent as ResourceTextContent, BinaryContent as ResourceBinaryContent
from typing import Optional,Any,Union
from pydantic import BaseModel

Content = Union['TextContent', 'ImageContent', 'AudioContent', 'EmbeddedResource']

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: dict[str,Any]
    outputSchema: Optional[dict[str,Any]]=None
    annotations: Optional['Annotations']=None


class ToolRequest(BaseModel):
    name: str
    arguments: dict[str,Any]

class TextContent(BaseModel):
    type: str = 'text'
    text: str

class ImageContent(BaseModel):
    type: str = 'image'
    data: str
    mimeType: str

class AudioContent(BaseModel):
    type: str = 'audio'
    data: str
    mimeType: str

class EmbeddedResource(BaseModel):
    type: str = 'resource'
    resource: ResourceTextContent | ResourceBinaryContent

class ToolResult(BaseModel):
    content: list[Content]
    isError: bool=False
    structuredContent: Optional[dict[str,Any]]=None

class Annotations(BaseModel):
    title: Optional[str]=None
    readOnlyHint: Optional[bool]=None
    destructiveHint: Optional[bool]=None
    idempotentHint: Optional[bool]=None
    openWorldHint: Optional[bool]=None