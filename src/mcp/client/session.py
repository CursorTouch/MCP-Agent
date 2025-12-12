from src.mcp.types.capabilities import ClientCapabilities, ClientRootsCapability, ClientSamplingCapability, ClientElicitationCapability
from src.mcp.types.json_rpc import JSONRPCRequest, JSONRPCNotification, Method, JSONRPCMessage, JSONRPCResponse
from src.mcp.types.resources import (
    ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceRequestParams, ReadResourceResult,
    ListResourceTemplatesRequest, ListResourceTemplatesResult,
    SubscribeRequest, SubscribeRequestParams,
    UnsubscribeRequest, UnsubscribeRequestParams
)
from src.mcp.types.initialize import InitializeResult, InitializeRequestParams, InitializeRequest
from src.mcp.types.tools import (
    Tool, CallToolRequest, CallToolRequestParams, CallToolResult,
    ListToolsRequest, ListToolsResult
)
from src.mcp.types.prompts import (
    Prompt, GetPromptResult, GetPromptRequest, GetPromptRequestParams,
    ListPromptsRequest, ListPromptsResult
)
from src.mcp.types.completion import CompleteRequest, CompleteRequestParams, CompleteResult
from src.mcp.types.elicitation import ElicitResult
from src.mcp.transport.base import BaseTransport
from src.mcp.types.sampling import CreateMessageResult
from src.mcp.types.info import Implementation
from src.mcp.types.common import RequestParams, PaginatedRequestParams
from src.mcp.types.logging import SetLevelRequest, SetLevelRequestParams
from src.mcp.types.ping import PingRequest
from src.mcp.types.notification import InitializedNotification
from src.mcp.types.roots import RootsListChangedNotification
from typing import Optional, Any
from uuid import uuid4

class Session:
    def __init__(self, transport: BaseTransport, client_info: Implementation) -> None:
        self.transport = transport
        self.client_info = client_info
        self.initialize_result: Optional[InitializeResult] = None

    async def connect(self) -> None:
        await self.transport.connect()

    def get_initialize_result(self) -> InitializeResult:
        return self.initialize_result

    async def initialize(self) -> InitializeResult:
        PROTOCOL_VERSION = "2024-11-05"
        
        # Capability Mapping
        # Roots
        roots = ClientRootsCapability(listChanged=True) if self.transport.callbacks.get("list_roots") else None
        
        # Sampling
        # Note: ClientSamplingCapability requires context/tools objects, defaulting to None/empty if implied supported
        # If callback exists, imply support?
        # Schema says empty object implies support for properties? No, they are Specific capabilities.
        # For now, if sampling callback exists, we declare empty capability object which implies support.
        sampling = ClientSamplingCapability() if self.transport.callbacks.get("sampling") else None
        
        # Elicitation
        # Similarly for elicitation
        elicitation = ClientElicitationCapability() if self.transport.callbacks.get("elicitation") else None

        params = InitializeRequestParams(
            clientInfo=self.client_info,
            capabilities=ClientCapabilities(
                roots=roots,
                sampling=sampling,
                elicitation=elicitation
            ),
            protocolVersion=PROTOCOL_VERSION
        )
        
        request = InitializeRequest(
            id=str(uuid4()),
            params=params
        )
        
        response = await self.transport.send_request(request=request)
        
        notification = InitializedNotification()
        await self.transport.send_notification(notification=notification)
        
        self.initialize_result = InitializeResult.model_validate(response.result)
        return self.initialize_result
    
    async def ping(self) -> bool:
        request = PingRequest(id=str(uuid4()))
        response = await self.transport.send_request(request=request)
        return response is not None

    async def prompts_list(self, params: Optional[PaginatedRequestParams] = None) -> ListPromptsResult:
        request = ListPromptsRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return ListPromptsResult.model_validate(response.result)
    
    async def prompts_get(self, params: GetPromptRequestParams) -> GetPromptResult:
        request = GetPromptRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return GetPromptResult.model_validate(response.result)
    
    async def resources_list(self, params: Optional[PaginatedRequestParams] = None) -> ListResourcesResult:
        request = ListResourcesRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return ListResourcesResult.model_validate(response.result)
    
    async def resources_read(self, params: ReadResourceRequestParams) -> ReadResourceResult:
        request = ReadResourceRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return ReadResourceResult.model_validate(response.result)
    
    async def resources_templates_list(self, params: Optional[PaginatedRequestParams] = None) -> ListResourceTemplatesResult:
        request = ListResourceTemplatesRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return ListResourceTemplatesResult.model_validate(response.result)
    
    async def resources_subscribe(self, params: SubscribeRequestParams) -> None:
        request = SubscribeRequest(
            id=str(uuid4()),
            params=params
        )
        await self.transport.send_request(request=request)

    async def resources_unsubscribe(self, params: UnsubscribeRequestParams) -> None:
        request = UnsubscribeRequest(
            id=str(uuid4()),
            params=params
        )
        await self.transport.send_request(request=request)
    
    async def tools_list(self, params: Optional[PaginatedRequestParams] = None) -> ListToolsResult:
        request = ListToolsRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return ListToolsResult.model_validate(response.result)
    
    async def tools_call(self, params: CallToolRequestParams) -> CallToolResult:
        request = CallToolRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return CallToolResult.model_validate(response.result)
    
    async def roots_list_changed(self) -> None:
        notification = RootsListChangedNotification()
        await self.transport.send_notification(notification=notification)

    async def completion_complete(self, params: CompleteRequestParams) -> CompleteResult:
        request = CompleteRequest(
            id=str(uuid4()),
            params=params
        )
        response = await self.transport.send_request(request=request)
        return CompleteResult.model_validate(response.result)

    async def logging_set_level(self, params: SetLevelRequestParams) -> None:
        request = SetLevelRequest(
            id=str(uuid4()),
            params=params
        )
        await self.transport.send_request(request=request)

    async def shutdown(self) -> None:
        await self.transport.disconnect()