from pydantic import BaseModel,Field

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
