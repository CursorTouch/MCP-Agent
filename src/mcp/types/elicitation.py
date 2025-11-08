from typing import Optional, Literal, Any, Protocol,Union
from pydantic import BaseModel,ConfigDict,Field
from src.mcp.types.json_rpc import Error

class ElicitationFn(Protocol):
    async def __call__(request:'ElicitRequest')->Union['ElicitResult',Error]:
        ...

class ElicitRequest(BaseModel):
    message:str
    requestedSchema:dict[str, Any]
    model_config=ConfigDict(extra='allow')

class ElicitResult(BaseModel):
    action:Literal["accept","decline","cancel"]
    content:dict[str, str|int|float|bool|None]|None=None