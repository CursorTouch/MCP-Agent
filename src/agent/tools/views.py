from pydantic import BaseModel,Field
from typing import Literal

class SharedBaseModel(BaseModel):
    class Config:
        extra = 'allow'

class Done(SharedBaseModel):
    answer:str = Field(...,description="the detailed final answer to the user query in proper markdown format",examples=["The task is completed successfully."])

class Connect(SharedBaseModel):
    name:str = Field(...,description="the name of the server to connect to",examples=["abc-mcp"])

class Disconnect(SharedBaseModel):
    name:str = Field(...,description="the name of the server to disconnect from",examples=["ucd-mcp"])

class Resource(SharedBaseModel):
    name:str = Field(...,description="the name of the server to access the resource from",examples=["ucd-mcp"])
    uri:str = Field(...,description="the URI of the resource to access",examples=["/resources/12345"])

class Search(SharedBaseModel):
    name:str = Field(...,description="only the keyword of the server to search for in the MCP registry",examples=["filesystem","docker","github"])
    limit:int = Field(10,description="Number of items per page (1-100)",gt=1,lt=100,example=10)
    # cursor:str = Field(description="Pagination cursor",example="server-cursor-123")
