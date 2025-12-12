from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal, Any, Union
from src.mcp.types.common import RequestId, RequestParams, PaginatedRequestParams, Result

TaskStatus = Literal["working", "input_required", "completed", "failed", "cancelled"]

class Task(BaseModel):
    createdAt: str
    lastUpdatedAt: str
    pollInterval: Optional[float] = None
    status: TaskStatus
    statusMessage: Optional[str] = None
    taskId: str
    ttl: Optional[float] = None
    
    model_config = ConfigDict(extra='allow')

class TaskMetadata(BaseModel):
    ttl: Optional[float] = None
    model_config = ConfigDict(extra='allow')

class RelatedTaskMetadata(BaseModel):
    taskId: str
    model_config = ConfigDict(extra='allow')

class CreateTaskResult(BaseModel):
    task: Task
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    model_config = ConfigDict(extra='allow')

class GetTaskRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tasks/get"] = "tasks/get"
    params: dict[str, str] # { taskId: string }
    
    model_config = ConfigDict(extra='allow')

class GetTaskResult(Result):
    # Result & Task. Pydantic doesn't support multiple inheritance of BaseModels easily for mixins in this way without redecuration
    # But I can inherit from Result (which has meta) and add Task fields.
    # OR inherit from Task and add Result fields.
    # Result has meta. Task has properties.
    # User says "GetTaskResult: Result & Task"
    # I will mix them.
    createdAt: str
    lastUpdatedAt: str
    pollInterval: Optional[float] = None
    status: TaskStatus
    statusMessage: Optional[str] = None
    taskId: str
    ttl: Optional[float] = None
    
    model_config = ConfigDict(extra='allow')

class GetTaskPayloadRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tasks/result"] = "tasks/result"
    params: dict[str, str] # { taskId: string }
    
    model_config = ConfigDict(extra='allow')

class GetTaskPayloadResult(BaseModel):
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    # [key: string]: unknown
    model_config = ConfigDict(extra='allow')

class ListTasksRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tasks/list"] = "tasks/list"
    params: Optional[PaginatedRequestParams] = None
    
    model_config = ConfigDict(extra='allow')

class ListTasksResult(BaseModel):
    tasks: list[Task]
    nextCursor: Optional[str] = None
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")
    
    model_config = ConfigDict(extra='allow')

class CancelTaskRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["tasks/cancel"] = "tasks/cancel"
    params: dict[str, str] # { taskId: string }
    
    model_config = ConfigDict(extra='allow')

class CancelTaskResult(Result):
    # Result & Task
    createdAt: str
    lastUpdatedAt: str
    pollInterval: Optional[float] = None
    status: TaskStatus
    statusMessage: Optional[str] = None
    taskId: str
    ttl: Optional[float] = None
    
    model_config = ConfigDict(extra='allow')
