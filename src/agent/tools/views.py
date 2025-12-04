from pydantic import BaseModel,Field

class Start(BaseModel):
    subtask:str=Field(description="The subtask to be solved by the thread")
    server_name:str=Field(description="The name of the server to be connected to")

class Switch(BaseModel):
    id:str=Field(description="The id of the thread to switch to")

class Stop(BaseModel):
    id:str=Field(description="The id of the thread to stop")
    result:str=Field(description="The result of the thread")
    error:str=Field(description="The error of the thread")