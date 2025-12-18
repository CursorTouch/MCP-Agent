from mistralai import HttpClient,AsyncHttpClient,RetryConfig,OptionalNullable, UserMessage, AssistantMessage, SystemMessage as MainMessage, TextChunk, ThinkChunk, ImageURL,ImageURLChunk, ResponseFormat, JSONSchema
from src.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ImageMessage
from src.llms.views import ChatLLMResponse, ChatLLMUsage
from src.llms.base import BaseChatLLM
from typing import Union,Dict,Type
from dataclasses import dataclass
from mistralai import Mistral
from pydantic import BaseModel
import logging

@dataclass
class ChatMistral(BaseChatLLM):
    def __init__(self, model: str, api_key: str, max_tokens: int|None=None, temperature: float = 0.7, server: Union[str, None] = None, server_url: Union[str, None] = None, url_params: Dict[str, str] = None, client: Type[HttpClient] = None, async_client: Type[AsyncHttpClient] = None,retry_config: OptionalNullable[RetryConfig] = None,timeout_ms: Union[int, None] = None,debug_logger: Union[logging.Logger, None] = None):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.server = server
        self.max_tokens = max_tokens
        self.server_url = server_url
        self.url_params = url_params
        self._client = client
        self.async_client = async_client
        self.retry_config = retry_config
        self.timeout_ms = timeout_ms
        self.debug_logger = debug_logger

    @property
    def client(self) -> Mistral:
        return Mistral(**{
            "api_key": self.api_key,
            "server": self.server,
            "server_url": self.server_url,
            "url_params": self.url_params,
            "client": self._client,
            "async_client": self.async_client,
            "retry_config": self.retry_config,
            "timeout_ms": self.timeout_ms,
            "debug_logger": self.debug_logger
        })

    @property
    def provider(self) -> str:
        return "mistral"
    
    @property
    def model_name(self) -> str:
        return self.model
    
    def serialize_messages(self, messages: list[BaseMessage]):
        serialized = []
        for message in messages:
            if isinstance(message, SystemMessage):
                content=[TextChunk(text=message.content)]
                serialized.append(MainMessage(content=content))
            elif isinstance(message, HumanMessage):
                content=[TextChunk(text=message.content)]
                serialized.append(UserMessage(content=content))
            elif isinstance(message, AIMessage):
                content=[TextChunk(text=message.content)]
                serialized.append(AssistantMessage(content=content))
            elif isinstance(message, ImageMessage):
                message.scale_images(scale=0.7)
                images=[f"data:{message.mime_type};base64,{image}" for image in message.convert_images("base64")]
                content=[
                    TextChunk(text=message.content),
                    *[ImageURLChunk(type="image_url",url=ImageURL(url=image,detail="auto")) for image in images]
                ]
                serialized.append(UserMessage(role="user",content=content))
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return serialized
    
    def invoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        completion=self.client.chat.complete(
            model=self.model,
            messages=self.serialize_messages(messages),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
            response_format=ResponseFormat(
                json_schema=JSONSchema(
                    name=structured_output.__class__.__name__,
                    description="Model output structured as JSON schema",
                    schema_definition=structured_output.model_json_schema()
                ),
                type="json_schema"
            ) if structured_output else None
        )
        if structured_output:
            content=structured_output.model_validate_json(completion.choices[0].message.content)
            thinking=None
        else:
            thinking_parts = []
            content_parts = []
            ai_contents=completion.choices[0].message.content
            
            if isinstance(ai_contents,str):
                content_parts.append(ai_contents)
            elif isinstance(ai_contents,list):
                for ai_content in ai_contents:
                    if isinstance(ai_content,TextChunk):
                        content_parts.append(ai_content.text)
                    elif isinstance(ai_content,ThinkChunk):
                        # Handle thinking whether it's a string or a list of chunks
                        if isinstance(ai_content.thinking, str):
                            thinking_parts.append(ai_content.thinking)
                        elif isinstance(ai_content.thinking, list):
                            for chunk in ai_content.thinking:
                                if hasattr(chunk, 'text'):
                                    thinking_parts.append(chunk.text)
                    else:
                        raise ValueError(f"Unsupported message type: {type(ai_content)}")
            else:
                raise ValueError(f"Unsupported message type: {type(ai_contents)}")

            content = AIMessage(content="".join(content_parts))
            thinking = "".join(thinking_parts) if thinking_parts else None

        return ChatLLMResponse(
            thinking=thinking,
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            )
        )

    async def ainvoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        completion=await self.client.chat.complete_async(
            model=self.model,
            messages=self.serialize_messages(messages),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False,
            response_format=ResponseFormat(
                json_schema=JSONSchema(
                    name=structured_output.__class__.__name__,
                    description="Model output structured as JSON schema",
                    schema_definition=structured_output.model_json_schema()
                ),
                type="json_schema"
            ) if structured_output else None
        )
        if structured_output:
            content=structured_output.model_validate_json(completion.choices[0].message.content)
            thinking=None
        else:
            thinking_parts = []
            content_parts = []
            ai_contents=completion.choices[0].message.content
            
            if isinstance(ai_contents,str):
                content_parts.append(ai_contents)
            elif isinstance(ai_contents,list):
                for ai_content in ai_contents:
                    if isinstance(ai_content,TextChunk):
                        content_parts.append(ai_content.text)
                    elif isinstance(ai_content,ThinkChunk):
                        # Handle thinking whether it's a string or a list of chunks
                        if isinstance(ai_content.thinking, str):
                            thinking_parts.append(ai_content.thinking)
                        elif isinstance(ai_content.thinking, list):
                            for chunk in ai_content.thinking:
                                if hasattr(chunk, 'text'):
                                    thinking_parts.append(chunk.text)
                    else:
                        raise ValueError(f"Unsupported message type: {type(ai_content)}")
            else:
                raise ValueError(f"Unsupported message type: {type(ai_contents)}")

            content = AIMessage(content="".join(content_parts))
            thinking = "".join(thinking_parts) if thinking_parts else None

        return ChatLLMResponse(
            thinking=thinking,
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            )
        )

    
