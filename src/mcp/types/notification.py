from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Literal
from src.mcp.types.common import RequestId, ProgressToken, NotificationParams

# Cancelled Notification
class CancelledNotificationParams(BaseModel):
    requestId: RequestId
    reason: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class CancelledNotification(BaseModel):
    method: Literal["notifications/cancelled"] = "notifications/cancelled"
    params: CancelledNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')

# Initialized Notification
class InitializedNotification(BaseModel):
    method: Literal["notifications/initialized"] = "notifications/initialized"
    params: Optional[NotificationParams] = None
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')

# Progress Notification
class ProgressNotificationParams(BaseModel):
    progressToken: ProgressToken
    progress: float
    total: Optional[float] = None
    message: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class ProgressNotification(BaseModel):
    method: Literal["notifications/progress"] = "notifications/progress"
    params: ProgressNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')

# Task Status Notification relative
# Note: Task definition is not strictly available in context, treating as generic dictionary mixin for now or just NotificationParams
# "TaskStatusNotificationParams: NotificationParams & Task"
# I will define it as inheriting from NotificationParams and allowing extra fields (which cover Task)
class TaskStatusNotificationParams(NotificationParams):
    # Task fields would go here or be dynamic
    model_config = ConfigDict(extra='allow')

class TaskStatusNotification(BaseModel):
    method: Literal["notifications/tasks/status"] = "notifications/tasks/status"
    params: TaskStatusNotificationParams
    jsonrpc: Literal["2.0"] = "2.0"
    model_config = ConfigDict(extra='allow')
