from pydantic import BaseModel,Field,ConfigDict
from typing import Optional,Any, Union
from enum import Enum
from src.mcp.types.common import RequestId, Error

JSONRPCError = Error

class JSONRPCRequest(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: RequestId
    method: str
    params: Optional[dict[str,Any]]=None

    model_config=ConfigDict(extra='allow')

class JSONRPCNotification(BaseModel):
    jsonrpc: str=Field(default="2.0")
    method: str
    params: Optional[dict[str,Any]]=None
    
    model_config=ConfigDict(extra='allow')

class JSONRPCResultResponse(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: RequestId
    result: Any

    model_config=ConfigDict(extra='allow')

class JSONRPCErrorResponse(BaseModel):
    jsonrpc: str=Field(default="2.0")
    id: Optional[RequestId]=None
    error: Error

    model_config=ConfigDict(extra='allow')

JSONRPCResponse = Union[JSONRPCResultResponse, JSONRPCErrorResponse]
JSONRPCMessage = Union[JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, BaseModel]

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
    
    # Task methods
    TASKS_GET = "tasks/get"
    TASKS_LIST = "tasks/list"
    TASKS_CANCEL = "tasks/cancel"
    TASKS_RESULT = "tasks/result"

    # Notification methods
    NOTIFICATION_INITIALIZED = "notifications/initialized"
    NOTIFICATION_CANCELLED = "notifications/cancelled"
    NOTIFICATION_PROGRESS = "notifications/progress"
    NOTIFICATION_MESSAGE = "notifications/message"
    
    # Task notifications
    NOTIFICATION_TASKS_STATUS = "notifications/tasks/status"
    
    # Elicitation notifications
    NOTIFICATION_ELICITATION_COMPLETE = "notifications/elicitation/complete"

    # Resource notifications
    NOTIFICATION_RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"
    NOTIFICATION_RESOURCES_UPDATED = "notifications/resources/updated"

    # Prompt notifications
    NOTIFICATION_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"

    # Tools notifications
    NOTIFICATION_TOOLS_LIST_CHANGED = "notifications/tools/list_changed"

    # Roots notifications
    NOTIFICATION_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"
    