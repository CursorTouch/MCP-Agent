from src.mcp.types.resources import BinaryContent as ResourceBinaryContent, TextContent as ResourceTextContent
from pydantic import BaseModel,ConfigDict
from typing import Optional, Any

class Prompt(BaseModel):
    name: str
    title: Optional[str]=None
    description: Optional[str]=None
    arguments: Optional[list['Argument']]=None

class Argument(BaseModel):
    name: str
    description: Optional[str]=None
    required: bool=False

    model_config=ConfigDict(extra='allow')

class PromptResult(BaseModel):
    description: Optional[str]=None
    messages: list['Message']

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
    type:str= 'resource'
    resource: ResourceTextContent | ResourceBinaryContent

class Message(BaseModel):
    role: str
    content: TextContent | ImageContent | AudioContent | EmbeddedResource

    model_config=ConfigDict(extra='allow')

# Request Types
class PromptsListRequest(BaseModel):
    cursor: Optional[str]=None
    model_config=ConfigDict(extra='allow')

class PromptsGetRequest(BaseModel):
    name: str
    arguments: Optional[dict[str, Any]]=None
    model_config=ConfigDict(extra='allow')

# Result Types
class PromptsListResult(BaseModel):
    prompts: list[Prompt]
    nextCursor: Optional[str]=None
    model_config=ConfigDict(extra='allow')