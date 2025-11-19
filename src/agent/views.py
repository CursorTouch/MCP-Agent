from typing import TypedDict,Any
from dataclasses import dataclass

class LLMResponse(TypedDict):
    thought:str
    action_name:str
    action_input:dict[str,Any]={}

@dataclass
class AgentResponse:
    is_success:bool=False
    response:str=''
    error:str=''