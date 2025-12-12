from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any

# Client Capabilities Parts

class ClientElicitationCapability(BaseModel):
    form: Optional[Any] = None # object
    url: Optional[Any] = None # object
    model_config = ConfigDict(extra='allow')

class ClientRootsCapability(BaseModel):
    listChanged: Optional[bool] = None
    model_config = ConfigDict(extra='allow')

class ClientSamplingCapability(BaseModel):
    context: Optional[Any] = None # object
    tools: Optional[Any] = None # object
    model_config = ConfigDict(extra='allow')

class ClientTasksElicitationRequestCapability(BaseModel):
    create: Optional[Any] = None
    model_config = ConfigDict(extra='allow')

class ClientTasksSamplingRequestCapability(BaseModel):
    createMessage: Optional[Any] = None
    model_config = ConfigDict(extra='allow')

class ClientTasksRequestsCapability(BaseModel):
    elicitation: Optional[ClientTasksElicitationRequestCapability] = None
    sampling: Optional[ClientTasksSamplingRequestCapability] = None
    model_config = ConfigDict(extra='allow')

class ClientTasksCapability(BaseModel):
    cancel: Optional[Any] = None
    list: Optional[Any] = None
    requests: Optional[ClientTasksRequestsCapability] = None
    model_config = ConfigDict(extra='allow')

class ClientCapabilities(BaseModel):
    elicitation: Optional[ClientElicitationCapability] = None
    experimental: Optional[dict[str, Any]] = None
    roots: Optional[ClientRootsCapability] = None
    sampling: Optional[ClientSamplingCapability] = None
    tasks: Optional[ClientTasksCapability] = None
    
    model_config = ConfigDict(extra='allow')

# Server Capabilities Parts

class ServerPromptsCapability(BaseModel):
    listChanged: Optional[bool] = None
    model_config = ConfigDict(extra='allow')

class ServerResourcesCapability(BaseModel):
    listChanged: Optional[bool] = None
    subscribe: Optional[bool] = None
    model_config = ConfigDict(extra='allow')

class ServerToolsCapability(BaseModel):
    listChanged: Optional[bool] = None
    model_config = ConfigDict(extra='allow')

class ServerTasksToolsRequestCapability(BaseModel):
    call: Optional[Any] = None
    model_config = ConfigDict(extra='allow')

class ServerTasksRequestsCapability(BaseModel):
    tools: Optional[ServerTasksToolsRequestCapability] = None
    model_config = ConfigDict(extra='allow')

class ServerTasksCapability(BaseModel):
    cancel: Optional[Any] = None
    list: Optional[Any] = None
    requests: Optional[ServerTasksRequestsCapability] = None
    model_config = ConfigDict(extra='allow')

class ServerCapabilities(BaseModel):
    completions: Optional[dict[str, Any]] = None # object
    experimental: Optional[dict[str, Any]] = None
    logging: Optional[dict[str, Any]] = None # object
    prompts: Optional[ServerPromptsCapability] = None
    resources: Optional[ServerResourcesCapability] = None
    tasks: Optional[ServerTasksCapability] = None
    tools: Optional[ServerToolsCapability] = None

    model_config = ConfigDict(extra='allow')