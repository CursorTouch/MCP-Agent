from pydantic import BaseModel,Field
from typing import Optional

class Start(BaseModel):
    subtask:str=Field(description="The explicit goal for the new thread to solve. MUST include all necessary data (filenames, IDs) as the child has no memory of the parent thread.",examples=['Fetch weather data for Singapore'])
    server_name:str=Field(description="The exact name of the MCP server to use.",examples=["weather-server"])

class Switch(BaseModel):
    id:str=Field(description="The target thread ID to switch context to.",examples=["thread-123"])

class Stop(BaseModel):
    id:Optional[str]=Field(default=None,description="The ID of the thread to stop. Defaults to current thread if omitted.",examples=["thread-123"])
    success:Optional[str]=Field(default="",description="A comprehensive summary of actions taken and data found. This is the ONLY context returned to the parent.",examples=["The weather in Singapore is sunny."])
    error:Optional[str]=Field(default="",description="Error message if the task failed.",examples=["Failed to fetch weather data."])

class Forget(BaseModel):
    id:str=Field(description="The ID of the COMPLETED or FAILED thread to remove from the process table.",examples=["thread-123"])