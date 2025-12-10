from src.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ImageMessage
from src.llms.views import ChatLLMResponse, ChatLLMUsage
from ollama import Client, AsyncClient,Image,Message
from src.llms.base import BaseChatLLM
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class ChatOllama(BaseChatLLM):
    def __init__(self,host: str|None=None, model: str|None=None, temperature: float = 0.7,timeout: int|None=None):
        self.host = host
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
    
    @property
    def provider(self) -> str:
        return "ollama"
    
    @property
    def client(self) -> Client:
        return Client(host=self.host,timeout=self.timeout)

    @property
    def async_client(self) -> AsyncClient:
        return AsyncClient(host=self.host,timeout=self.timeout)
    
    @property
    def model_name(self) -> str:
        return self.model
    
    def serialize_messages(self, messages: list[BaseMessage]) -> list[dict]:
        serialized = []
        for message in messages:
            if isinstance(message, SystemMessage):
                serialized.append(Message(role="system", content=message.content))
            elif isinstance(message, HumanMessage):
                serialized.append(Message(role="user", content=message.content))
            elif isinstance(message, AIMessage):
                serialized.append(Message(role="assistant", content=message.content))
            elif isinstance(message, ImageMessage):
                message.scale_images(scale=0.7)
                images=message.convert_images("bytes")
                serialized.append(Message(role="user", content=message.content,images=[Image(value=image) for image in images]))
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return serialized
    
    def invoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> str:
        completion=self.client.chat(
            model=self.model,
            stream=False,
            messages=self.serialize_messages(messages),
            format=structured_output.model_json_schema() if structured_output else "",
        )
        if structured_output:
            content=structured_output.model_validate_json(completion.message.content)
        else:
            content=AIMessage(content=completion.message.content)
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.get("prompt_eval_count"),
                completion_tokens=completion.get("eval_count"),
                total_tokens=completion.get("eval_count")+completion.get("prompt_eval_count"),
            )
        )
    async def ainvoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        completion=await self.async_client.chat(
            model=self.model,
            stream=False,
            messages=self.serialize_messages(messages),
            format=structured_output.model_json_schema() if structured_output else "",
        )
        if structured_output:
            content=structured_output.model_validate_json(completion.message.content)
        else:
            content=AIMessage(content=completion.message.content)
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.get("prompt_eval_count"),
                completion_tokens=completion.get("eval_count"),
                total_tokens=completion.get("eval_count")+completion.get("prompt_eval_count"),
            )
        )
        


        
    
