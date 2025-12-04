from dataclasses import dataclass,field
from src.messages import BaseMessage
from typing import Any, Literal
import uuid

@dataclass
class Thread:
    task: str=''
    server:str=''
    result: str|None=None
    error: str|None=None
    status: Literal["idle","progress","completed","started","stopped"]='idle'
    messages: list[BaseMessage] = field(default_factory=list)
    id: str = field(default_factory=lambda: f'thread-{uuid.uuid4().hex}')

@dataclass
class Action:
    name:str
    args:dict[str,Any]