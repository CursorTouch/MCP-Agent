from pydantic import BaseModel,Field,ConfigDict
from typing import Optional,Any
from enum import Enum

class JSONRPCRequest(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: Optional[str|int]=None
    method: Optional['Method']=None
    params: Optional[dict[str,Any]]=None

    model_config=ConfigDict(extra='allow')

class JSONRPCNotification(BaseModel):
    jsonrpc: str=Field(default="2.0")
    method: Optional['Method']=None
    params: Optional[dict[str,Any]]=None

class JSONRPCResponse(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: Optional[str|int]=None
    result: Optional[dict[str,Any]]=None

    model_config=ConfigDict(extra='allow')

class JSONRPCError(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: Optional[str|int]=None
    error: 'Error'

    model_config=ConfigDict(extra='allow')

class Error(BaseModel):
    code: int
    message: str
    data: Optional[Any]=None

    model_config=ConfigDict(extra='allow')

class Method(str,Enum):
    # Ping
    PING = "ping"

    # Initialize
    INITIALIZE = "initialize"

    # Resource methods
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_SUBSCRIBE = "resources/subscribe"
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"
    RESOURCES_TEMPLATES_LIST = "resources/templates/list"

    # Tool methods
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"

    # Logging methods
    LOGGING_SET_LEVEL = "logging/setLevel"

    #Completion methods
    COMPLETION_COMPLETE = "completion/complete"

    # Prompt methods
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"

    # Elicitation methods
    ELICITATION_CREATE = "elicitation/create"

    # Sampling methods
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"

    # Root methods
    ROOTS_LIST="roots/list"

    # Notification methods
    NOTIFICATION_INITIALIZED = "notifications/initialized"
    NOTIFICATION_CANCELLED = "notifications/cancelled"
    NOTIFICATION_PROGRESS = "notifications/progress"
    NOTIFICATION_MESSAGE = "notifications/message"

    # Resource notifications
    NOTIFICATION_RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"
    NOTIFICATION_RESOURCES_UPDATED = "notifications/resources/updated"

    # Prompt notifications
    NOTIFICATION_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"

    # Tools notifications
    NOTIFICATION_TOOLS_LIST_CHANGED = "notifications/tools/list_changed"

    # Roots notifications
    NOTIFICATION_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"
    