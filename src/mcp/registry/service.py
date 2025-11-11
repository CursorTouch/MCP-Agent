from src.mcp.types.registry import (ListServersRequest,ListServersResponse,
ListServerVersionsRequest,ListServerVersionsResponse,HealthCheckRequest,
HealthCheckResponse,PingRequest,PingResponse,VersionRequest,VersionResponse,
SpecificServerVersionRequest,SpecificServerVersionResponse,ErrorResponse) 
from httpx import AsyncClient,Client,HTTPStatusError
from typing import Literal

class MCPRegistry:
    def __init__(self,version:Literal["v0","v0.1"]="v0.1"):
        self.base_url=f"https://registry.modelcontextprotocol.io/{version}"
        self.headers={
            "Accept":"application/json, application/problem+json",
        }

    @property
    def aclient(self)->AsyncClient:
        return AsyncClient(base_url=self.base_url,headers=self.headers)
    
    @property
    def client(self)->Client:
        return Client(base_url=self.base_url,headers=self.headers)
    
    async def list_servers(self,request:ListServersRequest)->ListServersResponse:
        response=await self.aclient.get("/servers",params=request.model_dump(exclude_none=True))
        return ListServersResponse(**response.json())
    
    async def list_server_versions(self,request:ListServerVersionsRequest)->ListServerVersionsResponse:
        try:
            response=await self.aclient.get(f"/servers/{request.serverName}/versions")
            response.raise_for_status()
        except HTTPStatusError:
            return ErrorResponse(**response.json())
        return ListServerVersionsResponse(**response.json())
    
    async def specific_server_version(self,request:SpecificServerVersionRequest)->SpecificServerVersionResponse:
        try:
            response=await self.aclient.get(f"/servers/{request.server_id}/versions/{request.version}")
            response.raise_for_status()
        except HTTPStatusError:
            return ErrorResponse(**response.json())
        return SpecificServerVersionResponse(**response.json())

    async def health_check(self,request:HealthCheckRequest|None=None)->HealthCheckResponse:
        response=await self.aclient.get(f"/health")
        return HealthCheckResponse(**response.json())
    
    async def ping(self,request:PingRequest|None=None)->PingResponse:
        response=await self.aclient.get(f"/ping")
        return PingResponse(**response.json())
    
    async def version(self,request:VersionRequest|None=None)->VersionResponse:
        response=await self.aclient.get(f"/version")
        return VersionResponse(**response.json())
