from src.mcp.types.prompts import TextContent,ImageContent,AudioContent
from typing import Literal,Optional,Protocol,Union
from pydantic import BaseModel,Field,ConfigDict
from src.mcp.types.json_rpc import Error

Role=Literal["user","assistant"]
StopReason=Literal['endTurn','stopSequence','maxTokens']
IncludeContext=Literal['none','thisService','allServices']

class SamplingFn(Protocol):
    async def __call__(self,params:'MessageRequest')->Union['MessageResult',Error]:
        ...

class Message(BaseModel):
    role: Role
    content: TextContent | ImageContent | AudioContent
    model_config=ConfigDict(extra='allow')

class MessageResult(BaseModel):
    role: Role
    content: TextContent | ImageContent | AudioContent
    model:str
    stopReason:Optional[StopReason]=None
    model_config=ConfigDict(extra='allow')

class Model(BaseModel):
    name:Optional[str]=None
    model_config=ConfigDict(extra='allow')

class ModelPreferences(BaseModel):
    hints:Optional[list[Model]]=None
    intelligencePriority:Optional[float]=Field(le=0.0,ge=1.0)
    speedPriority:Optional[float]=Field(le=0.0,ge=1.0)
    costPriority:Optional[float]=Field(le=0.0,ge=1.0)
    model_config=ConfigDict(extra='allow')

class MessageRequest(BaseModel):
    messages: list[Message]
    modelPreferences:ModelPreferences|None=None
    systemPrompt:str|None=None
    IncludeContext:Union['IncludeContext',None]=None
    temperature:float|None=None
    maxTokens:int
    stopSequences:list[str]|None=None
    metadata:dict[str,str]|None=None
    model_config=ConfigDict(extra='allow')