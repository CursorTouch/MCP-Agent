from src.mcp.types.capabilities import ClientCapabilities, RootCapability, SamplingCapability, ElicitationCapability
from src.mcp.types.json_rpc import JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, Method
from src.mcp.types.resources import Resource, ResourceResult, ResourceTemplate
from src.mcp.types.initialize import InitializeResult,InitializeParams
from src.mcp.types.tools import Tool, ToolRequest, ToolResult
from src.mcp.types.prompts import Prompt, PromptResult
from src.mcp.types.elicitation import ElicitResult
from src.mcp.transport.base import BaseTransport
from src.mcp.types.sampling import MessageResult
from src.mcp.types.info import ClientInfo
from typing import Optional,Any,Callable
from src.mcp.exception import MCPError
from src.mcp.types.roots import Root
from uuid import uuid4

class Session:
    def __init__(self,transport:BaseTransport,client_info:ClientInfo,)->None:
        self.id=str(uuid4())
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
        request=JSONRPCRequest(id=self.id,method=Method.INITIALIZE,params=params.model_dump(exclude_none=True))
        response=await self.transport.send_request(request=request)
        notification=JSONRPCNotification(method=Method.NOTIFICATION_INITIALIZED)
        await self.transport.send_notification(notification=notification)
        self.initialize_result=InitializeResult.model_validate(response.result)
        return InitializeResult.model_validate(response.result)
    
    async def ping(self)->bool:
        request=JSONRPCRequest(id=self.id,method=Method.PING)
        response=await self.transport.send_request(request=request)
        return response is not None

    async def prompts_list(self)->list[Prompt]:
        request=JSONRPCRequest(id=self.id,method=Method.PROMPTS_LIST)
        response=await self.transport.send_request(request=request)
        return [Prompt.model_validate(prompt) for prompt in response.result.get("prompts")]
    
    async def prompts_get(self,name:str,arguments:Optional[dict[str,Any]]=None)->PromptResult:
        request=JSONRPCRequest(id=self.id,method=Method.PROMPTS_GET,params={"name":name,"arguments":arguments})
        response=await self.transport.send_request(request=request)
        return PromptResult.model_validate(response.result)
    
    async def resources_list(self,cursor:Optional[str]=None)->list[Resource]:
        request=JSONRPCRequest(id=self.id,method=Method.RESOURCES_LIST,params={"cursor":cursor} if cursor else {})
        response=await self.transport.send_request(request=request)
        return [Resource.model_validate(resource) for resource in response.result.get("resources")]
    
    async def resources_read(self,uri:str)->ResourceResult:
        request=JSONRPCRequest(id=self.id,method=Method.RESOURCES_READ,params={"uri":uri})
        response=await self.transport.send_request(request=request)
        return [ResourceResult.model_validate(resource) for resource in response.result.get("contents")]
    
    async def resources_templates_list(self)->list[ResourceTemplate]:
        request=JSONRPCRequest(id=self.id,method=Method.RESOURCES_TEMPLATES_LIST)
        response=await self.transport.send_request(request=request)
        return [ResourceTemplate.model_validate(template) for template in response.result.get("resourceTemplates")]
    
    async def resources_subscribe(self,uri:str)->None:
        request=JSONRPCRequest(id=self.id,method=Method.RESOURCES_SUBSCRIBE,params={"uri":uri})
        await self.transport.send_request(request=request)

    async def resources_unsubscribe(self,uri:str)->None:
        request=JSONRPCRequest(id=self.id,method=Method.RESOURCES_UNSUBSCRIBE,params={"uri":uri})
        await self.transport.send_request(request=request)
    
    async def tools_list(self,cursor:Optional[str]=None)->list[Tool]:
        message=JSONRPCRequest(id=self.id,method=Method.TOOLS_LIST,params={"cursor":cursor} if cursor else {})
        response=await self.transport.send_request(request=message)
        return [Tool.model_validate(tool) for tool in response.result.get("tools")]
    
    async def tools_call(self,tool_name:str,**arguments)->ToolResult:
        tool_request=ToolRequest(name=tool_name,arguments=arguments)
        message=JSONRPCRequest(id=self.id,method=Method.TOOLS_CALL,params=tool_request.model_dump())
        response=await self.transport.send_request(request=message)
        return ToolResult.model_validate(response.result)
    
    async def roots_list_changed(self)->None:
        notification=JSONRPCNotification(method=Method.NOTIFICATION_ROOTS_LIST_CHANGED)
        await self.transport.send_notification(notification=notification)

    async def shutdown(self)->None:
        await self.transport.disconnect()