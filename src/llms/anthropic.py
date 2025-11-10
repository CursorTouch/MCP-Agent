from anthropic.types import Message,MessageParam,ImageBlockParam,Base64ImageSourceParam,TextBlockParam,CacheControlEphemeralParam
from src.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ImageMessage
from src.llms.views import ChatLLMResponse, ChatLLMUsage
from anthropic import Anthropic,AsyncAnthropic
from src.llms.base import BaseChatLLM
from dataclasses import dataclass
from pydantic import BaseModel
from httpx import Client

@dataclass
class ChatAnthropic(BaseChatLLM):
    def __init__(self, model: str, api_key: str, temperature: float = 0.7, max_tokens: int = 8192, auth_token: str | None = None, base_url: str | None = None, timeout: float | None = None, max_retries: int = 3, default_headers: dict[str, str] | None = None, default_query: dict[str, object] | None = None, http_client: Client | None = None, strict_response_validation: bool = False):
        self.model = model
        self.api_key = api_key
        self.auth_token = auth_token
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = default_headers
        self.default_query = default_query
        self.http_client = http_client
        self.strict_response_validation = strict_response_validation

    @property
    def client(self):
        return Anthropic(**{
            "api_key": self.api_key,
            "auth_token": self.auth_token,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
            "_strict_response_validation": self.strict_response_validation
        })
    
    @property
    def async_client(self):
        return AsyncAnthropic(**{
            "api_key": self.api_key,
            "auth_token": self.auth_token,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
            "_strict_response_validation": self.strict_response_validation
        })

    @property
    def provider(self):
        return "anthropic"

    @property
    def model_name(self):
        return self.model
    
    def serialize_messages(self, messages: list[BaseMessage]):
        system_instruction = None
        serialized = []
        for message in messages:
            if isinstance(message, SystemMessage):
                system_instruction = [TextBlockParam(
                    type="text",text=message.content,
                    cache_control=CacheControlEphemeralParam(type="ephemeral",ttl='5m')
                )]
            elif isinstance(message, HumanMessage):
                content=[TextBlockParam(type="text",text=message.content)]
                serialized.append(MessageParam(role="user",content=content))
            elif isinstance(message, AIMessage):
                content=[TextBlockParam(type="text",text=message.content)]
                serialized.append(MessageParam(role="assistant",content=content))
            elif isinstance(message, ImageMessage):
                message.scale_images(scale=0.7)
                images=[f"data:{message.mime_type};base64,{image}" for image in message.convert_images("base64")]
                content=[
                    TextBlockParam(type="text",text=message.content),
                    *[ImageBlockParam(type="image",source=Base64ImageSourceParam(
                        type="base64",data=image,media_type=message.mime_type
                    )) for image in images]
                ]
                serialized.append(MessageParam(role="user",content=content))
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return system_instruction,serialized
    
    def invoke(self, messages: list[BaseMessage], structured_output:BaseModel|None = None):
        system_instruction, messages = self.serialize_messages(messages)
        completion = self.client.messages.create(
            max_tokens=self.max_tokens,
            model=self.model,
            system=system_instruction,
            messages=messages,
            temperature=self.temperature,
        )

        if not isinstance(completion,Message):
            raise ValueError("Unexpected response type from Anthropic API")
        text_block = completion.content[0]
        content=text_block.text
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.input_tokens,
                completion_tokens=completion.usage.output_tokens,
                total_tokens=completion.usage.input_tokens+completion.usage.output_tokens
            )
        )

    async def ainvoke(self, messages: list[BaseMessage], structured_output:BaseModel|None = None):
        system_instruction, messages = self.serialize_messages(messages)
        completion = await self.async_client.messages.create(
            max_tokens=self.max_tokens,
            model=self.model,
            system=system_instruction,
            messages=messages,
            temperature=self.temperature,
        )

        if not isinstance(completion,Message):
            raise ValueError("Unexpected response type from Anthropic API")
        text_block = completion.content[0]
        content=text_block.text
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.input_tokens,
                completion_tokens=completion.usage.output_tokens,
                total_tokens=completion.usage.input_tokens+completion.usage.output_tokens
            )
        )