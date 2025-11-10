from openai.types.chat import ChatCompletionAssistantMessageParam,ChatCompletionUserMessageParam,ChatCompletionContentPartTextParam,ChatCompletionContentPartImageParam,ChatCompletionSystemMessageParam
from openai.types.shared_params.response_format_json_schema import JSONSchema, ResponseFormatJSONSchema
from src.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ImageMessage
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from src.llms.views import ChatLLMResponse, ChatLLMUsage
from openai import OpenAI, AsyncOpenAI
from src.llms.base import BaseChatLLM
from dataclasses import dataclass
from pydantic import BaseModel
from httpx import Client

@dataclass
class ChatOpenAI(BaseChatLLM):
    def __init__(self, model: str, api_key: str|None=None, organization: str|None=None, project: str|None=None, base_url: str|None=None, websocket_base_url: str|None=None, temperature: float = 0.7,max_retries: int = 3,timeout: int|None=None, default_headers: dict[str, str] | None = None, default_query: dict[str, object] | None = None, http_client: Client | None = None, strict_response_validation: bool = False):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_retries = max_retries
        self.organization = organization
        self.project = project
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = default_headers
        self.default_query = default_query
        self.http_client = http_client
        self.websocket_base_url = websocket_base_url
        self.strict_response_validation = strict_response_validation
    
    @property
    def client(self):
        return OpenAI(**{
            "api_key": self.api_key,
            "base_url": self.base_url,
            "max_retries": self.max_retries,
            "websocket_base_url": self.websocket_base_url,
            "timeout": self.timeout,
            "organization": self.organization,
            "project": self.project,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
            "_strict_response_validation": self.strict_response_validation
        })
    
    @property
    def async_client(self):
        return AsyncOpenAI(**{
            "api_key": self.api_key,
            "base_url": self.base_url or 'https://api.openai.com/v1',
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "organization": self.organization,
            "project": self.project,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
            "_strict_response_validation": self.strict_response_validation
        })
    
    @property
    def provider(self):
        return "openai"
    
    @property
    def model_name(self):
        return self.model
    
    def serialize_messages(self, messages: list[BaseMessage]):
        serialized = []
        for message in messages:
            if isinstance(message, SystemMessage):
                content=[ChatCompletionContentPartTextParam(type="text",text=message.content)]
                serialized.append(ChatCompletionSystemMessageParam(role="system",content=content))
            elif isinstance(message, HumanMessage):
                content=[ChatCompletionContentPartTextParam(type="text",text=message.content)]
                serialized.append(ChatCompletionUserMessageParam(role="user",content=content))
            elif isinstance(message, AIMessage):
                content=[ChatCompletionContentPartTextParam(type="text",text=message.content)]
                serialized.append(ChatCompletionAssistantMessageParam(role="assistant",content=content))
            elif isinstance(message, ImageMessage):
                message.scale_images(scale=0.7)
                images=[f"data:{message.mime_type};base64,{image}" for image in message.convert_images("base64")]
                content=[
                    ChatCompletionContentPartTextParam(type="text",text=message.content),
                    *[ChatCompletionContentPartImageParam(type="image_url",url=ImageURL(url=image,detail="auto")) for image in images]
                ]
                serialized.append(ChatCompletionUserMessageParam(role="user",content=content))
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return serialized
    
    def invoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> str:
        completion=self.client.chat.completions.create(
            model=self.model,
            messages=self.serialize_messages(messages),
            temperature=self.temperature,
            response_format=ResponseFormatJSONSchema(
                type="json_schema",
                json_schema=JSONSchema(
                    name=structured_output.__class__.__name__,
                    description="Model output structured as JSON schema",
                    schema=structured_output.model_json_schema()
                )
            ) if structured_output else None
        )
        content=completion.choices[0].message.content
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            )
        )
    
    async def ainvoke(self, messages: list[BaseMessage],structured_output:BaseModel|None=None) -> ChatLLMResponse:
        completion=await self.async_client.chat.completions.create(
            model=self.model,
            messages=self.serialize_messages(messages),
            temperature=self.temperature,
            response_format=ResponseFormatJSONSchema(
                type="json_schema",
                json_schema=JSONSchema(
                    name=structured_output.__class__.__name__,
                    description="Model output structured as JSON schema",
                    schema=structured_output.model_json_schema()
                )
            ) if structured_output else None
        )
        content=completion.choices[0].message.content
        return ChatLLMResponse(
            content=content,
            usage=ChatLLMUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            )
        )