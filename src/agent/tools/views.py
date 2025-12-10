from pydantic import BaseModel,Field
from typing import Optional

class Start(BaseModel):
    subtask:str=Field(description="The subtask to be solved by the thread")
    server_name:str=Field(description="The name of the server to be connected to")

class Switch(BaseModel):
    id:str=Field(description="The id of the thread to switch to")

class Stop(BaseModel):
    id:Optional[str]=Field(...,description="The id of the thread to stop")
    result:Optional[str]=Field(default="",description="The result of the thread")
    error:Optional[str]=Field(default="",description="The error of the thread")