from typing import Protocol,runtime_checkable,overload
from src.llms.views import ChatLLMResponse
from src.messages import BaseMessage
from pydantic import BaseModel
from src.tool import Tool

@runtime_checkable
class BaseChatLLM(Protocol):

    @property
    def model_name(self) -> str:
        ...

    @property
    def provider(self) -> str:
        ...

    @overload
    def invoke(self, tools:list[Tool], messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        ...

    @overload
    async def ainvoke(self, tools:list[Tool], messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        ...


    