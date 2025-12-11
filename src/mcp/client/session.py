from src.mcp.types.capabilities import ClientCapabilities, RootCapability, SamplingCapability, ElicitationCapability
from src.mcp.types.json_rpc import JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, Method
from src.mcp.types.resources import Resource, ResourceResult, ResourceTemplate, ResourcesListRequest, ResourcesReadRequest, ResourcesTemplatesListRequest, ResourcesSubscribeRequest, ResourcesUnsubscribeRequest, ResourcesListResult, ResourcesTemplatesListResult
from src.mcp.types.initialize import InitializeResult,InitializeParams
from src.mcp.types.tools import Tool, ToolRequest, ToolResult, ToolsListRequest, ToolsListResult
from src.mcp.types.prompts import Prompt, PromptResult, PromptsListRequest, PromptsGetRequest, PromptsListResult
from src.mcp.types.elicitation import ElicitResult
from src.mcp.transport.base import BaseTransport
from src.mcp.types.sampling import MessageResult
from src.mcp.types.info import ClientInfo
from typing import Optional,Any,Callable
from src.mcp.exception import MCPError
from src.mcp.types.roots import Root
from uuid import uuid4

class MCPSession:
    def __init__(self,transport:BaseTransport,client_info:ClientInfo,)->None:
        self.transport=transport
        self.client_info=client_info
        self.initialize_result:Optional[InitializeResult]=None

    async def connect(self)->None:
        await self.transport.connect()

    def get_initialize_result(self)->InitializeResult:
        return self.initialize_result

    async def initialize(self,)->InitializeResult:
        PROTOCOL_VERSION="2024-11-05"
        roots=RootCapability(listChanged=True) if self.transport.callbacks.get("list_roots") else None
        sampling=SamplingCapability() if self.transport.callbacks.get("sampling") else None
        elicitation=ElicitationCapability() if self.transport.callbacks.get("elicitation") else None
        params=InitializeParams(clientInfo=self.client_info,capabilities=ClientCapabilities(roots=roots,sampling=sampling,elicitation=elicitation),protocolVersion=PROTOCOL_VERSION)
        request=JSONRPCRequest(id=str(uuid4()),method=Method.INITIALIZE,params=params.model_dump(exclude_none=True))
        response=await self.transport.send_request(request=request)
        notification=JSONRPCNotification(method=Method.NOTIFICATION_INITIALIZED)
        await self.transport.send_notification(notification=notification)
        self.initialize_result=InitializeResult.model_validate(response.result)
        return self.initialize_result
    
    async def ping(self)->bool:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.PING)
        response=await self.transport.send_request(request=request)
        return response is not None

    async def prompts_list(self, params:Optional[PromptsListRequest]=None)->PromptsListResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.PROMPTS_LIST, params=params.model_dump(exclude_none=True) if params else None)
        response=await self.transport.send_request(request=request)
        return PromptsListResult.model_validate(response.result)
    
    async def prompts_get(self,params:PromptsGetRequest)->PromptResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.PROMPTS_GET,params=params.model_dump(exclude_none=True))
        response=await self.transport.send_request(request=request)
        return PromptResult.model_validate(response.result)
    
    async def resources_list(self,params:Optional[ResourcesListRequest]=None)->ResourcesListResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.RESOURCES_LIST,params=params.model_dump(exclude_none=True) if params else None)
        response=await self.transport.send_request(request=request)
        return ResourcesListResult.model_validate(response.result)
    
    async def resources_read(self,params:ResourcesReadRequest)->ResourceResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.RESOURCES_READ,params=params.model_dump(exclude_none=True))
        response=await self.transport.send_request(request=request)
        return ResourceResult.model_validate(response.result)
    
    async def resources_templates_list(self, params:Optional[ResourcesTemplatesListRequest]=None)->ResourcesTemplatesListResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.RESOURCES_TEMPLATES_LIST, params=params.model_dump(exclude_none=True) if params else None)
        response=await self.transport.send_request(request=request)
        return ResourcesTemplatesListResult.model_validate(response.result)
    
    async def resources_subscribe(self,params:ResourcesSubscribeRequest)->None:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.RESOURCES_SUBSCRIBE,params=params.model_dump(exclude_none=True))
        await self.transport.send_request(request=request)

    async def resources_unsubscribe(self,params:ResourcesUnsubscribeRequest)->None:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.RESOURCES_UNSUBSCRIBE,params=params.model_dump(exclude_none=True))
        await self.transport.send_request(request=request)
    
    async def tools_list(self,params:Optional[ToolsListRequest]=None)->ToolsListResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.TOOLS_LIST,params=params.model_dump(exclude_none=True) if params else None)
        response=await self.transport.send_request(request=request)
        return ToolsListResult.model_validate(response.result)
    
    async def tools_call(self,params:ToolRequest)->ToolResult:
        request=JSONRPCRequest(id=str(uuid4()),method=Method.TOOLS_CALL,params=params.model_dump(exclude_none=True))
        response=await self.transport.send_request(request=request)
        return ToolResult.model_validate(response.result)
    
    async def roots_list_changed(self)->None:
        notification=JSONRPCNotification(method=Method.NOTIFICATION_ROOTS_LIST_CHANGED)
        await self.transport.send_notification(notification=notification)

    async def shutdown(self)->None:
        await self.transport.disconnect()