from src.agent.tools.views import Start,Switch,Stop
from src.tool.service import Tool
from typing import cast

@Tool(name="Start Tool",args_schema=Start)
async def start_tool(subtask:str,server_name:str,**kwargs):
    '''Start a new thread and become the active thread to solve a subtask'''
    pass
    
@Tool(name="Switch Tool",args_schema=Switch)
def switch_tool(id:str,**kwargs):
    '''Switch to another thread from the current thread'''
    pass

@Tool(name="Stop Tool",args_schema=Stop)
def stop_tool(id:str,result:str,error:str,**kwargs):
    '''Stop a specific thread and switch to the previous thread'''
    pass