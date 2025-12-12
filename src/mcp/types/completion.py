from typing import Optional, Union, Literal, Any
from pydantic import BaseModel, ConfigDict, Field
from src.mcp.types.common import RequestId, Result

# References
class PromptReference(BaseModel):
    name: str  
    title: Optional[str] = None
    type: Literal["ref/prompt"] = "ref/prompt"
    model_config = ConfigDict(extra='allow')

class ResourceTemplateReference(BaseModel):
    uri: str
    type: Literal["ref/resource"] = "ref/resource"
    model_config = ConfigDict(extra='allow')

class CompletionArgument(BaseModel):
    name: str
    value: str
    model_config = ConfigDict(extra='allow')

class CompletionContext(BaseModel):
    arguments: Optional[dict[str, str]] = None
    model_config = ConfigDict(extra='allow')

# Request Params
class CompleteRequestParams(BaseModel):
    argument: CompletionArgument
    context: Optional[CompletionContext] = None
    ref: Union[PromptReference, ResourceTemplateReference]
    meta: Optional[dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = ConfigDict(extra='allow')

class CompleteRequest(BaseModel):
    id: RequestId
    jsonrpc: Literal["2.0"] = "2.0"
    method: Literal["completion/complete"] = "completion/complete"
    params: CompleteRequestParams
    model_config = ConfigDict(extra='allow')

# Result
class CompletionValues(BaseModel):
    hasMore: Optional[bool] = None
    total: Optional[int] = None
    # Must not exceed 100 items
    values: list[str] 
    model_config = ConfigDict(extra='allow')

class CompleteResult(Result):
    completion: CompletionValues
    model_config = ConfigDict(extra='allow')
