from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Metadata(BaseModel):
    count: int
    nextCursor: Optional[str] = None  # ✅ made optional

class OfficialMeta(BaseModel):
    isLatest: Optional[bool] = None
    publishedAt: Optional[datetime] = None
    status: Optional[str] = None
    updatedAt: Optional[datetime] = None

class RegistryMeta(BaseModel):
    official: Optional[OfficialMeta] = None

class VariableDefinition(BaseModel):
    choices: Optional[List[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None
    isRequired: Optional[bool] = None
    isSecret: Optional[bool] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None

class Variable(BaseModel):
    choices: Optional[List[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None
    isRequired: Optional[bool] = None
    isSecret: Optional[bool] = None
    name: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    variables: Optional[Dict[str, VariableDefinition]] = None

class Transport(BaseModel):
    type: str
    url: Optional[HttpUrl] = None  # ✅ optional
    headers: Optional[List[Variable]] = None

class Package(BaseModel):
    environmentVariables: Optional[List[Variable]] = None
    fileSha256: Optional[str] = None
    identifier: Optional[str] = None
    packageArguments: Optional[List[Variable]] = None
    registryBaseUrl: Optional[HttpUrl] = None
    registryType: Optional[str] = None
    runtimeArguments: Optional[List[Variable]] = None
    runtimeHint: Optional[str] = None
    transport: Optional[Transport] = None
    version: Optional[str] = None

class Repository(BaseModel):
    id: Optional[str] = None  # ✅ optional
    source: Optional[str] = None
    subfolder: Optional[str] = None  # ✅ optional
    url: Optional[HttpUrl] = None

class Icon(BaseModel):
    mimeType: Optional[str] = None
    sizes: Optional[List[str]] = None
    src: Optional[HttpUrl] = None
    theme: Optional[str] = None

class ServerDefinition(BaseModel):
    schema_: Optional[HttpUrl] = None  # $schema renamed to schema_
    _meta: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icons: Optional[List[Icon]] = None  # ✅ optional
    packages: Optional[List[Package]] = None
    remotes: Optional[List[Transport]] = None  # ✅ optional
    repository: Optional[Repository] = None
    title: Optional[str] = None  # ✅ optional
    version: Optional[str] = None
    websiteUrl: Optional[HttpUrl] = None  # ✅ optional

class Server(BaseModel):
    _meta: Optional[Dict[str, Any]] = None
    server: ServerDefinition

class ListServersResponse(BaseModel):
    metadata: Metadata
    servers: List[Server]

class ListServersRequest(BaseModel):
    cursor: Optional[str] = Field(None,description="Pagination cursor",example="server-cursor-123")
    limit: Optional[int] = Field(30,description="Number of items per page (1-100)",gt=1,lt=100,example=50)
    search: Optional[str] = Field(None,description="Search servers by name (substring match)",example="filesystem")
    updated_since: Optional[datetime] = Field(None,description="Filter servers updated since timestamp (RFC3339 datetime)",example="2025-08-07T13:15:04.280Z")
    version: Optional[str] = Field(None,description="Filter by version ('latest' or an exact version like '1.2.3')",example="latest")

class ListServerVersionsRequest(BaseModel):
    serverName: str =Field(...,description="URL-encoded server name",example="filesystem-mcp")

class ListServerVersionsResponse(BaseModel):
    metadata: Metadata
    servers: List[Server]

class SpecificServerVersionRequest(BaseModel):
    serverName: str =Field(...,description="URL-encoded server name",example="filesystem-mcp")
    version: str =Field(...,description="Server version",example="1.2.3")

class SpecificServerVersionResponse(BaseModel):
    _meta:Dict[str,Any]
    server:ServerDefinition

class HealthCheckRequest(BaseModel):
    pass

class HealthCheckResponse(BaseModel):
    github_client_id: Optional[str] = None
    status:str

class PingRequest(BaseModel):
    pass

class PingResponse(BaseModel):
    pong:bool

class VersionRequest(BaseModel):
    pass

class VersionResponse(BaseModel):
    build_time:str
    git_commit:str
    version:str

class ErrorResponse(BaseModel):
    title:str
    status:int
    detail:str