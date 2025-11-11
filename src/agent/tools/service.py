from src.agent.tools.views import Done,Connect,Disconnect
from src.mcp.client import MCPClient
from src.tool import Tool

@Tool('Done Tool',args_schema=Done)
async def done_tool(answer:str,**kwargs):
    '''To indicate that the task is completed'''
    return answer

@Tool('Connect Tool',args_schema=Connect)
async def connect_tool(name:str,**kwargs):
    '''Connect to a specific MCP server'''
    client:MCPClient=kwargs['client']
    if name.lower() in client.sessions:
        return f'Server {name.lower()} already connected.'
    session=await client.create_session(name.lower())   
    client.sessions[name.lower()]=session
    return f'{name.lower()} now connected.'

@Tool('Disconnect Tool',args_schema=Disconnect)
async def disconnect_tool(name:str,**kwargs):
    '''Disconnect from a specific MCP server'''
    client:MCPClient=kwargs['client']
    if name.lower() not in client.sessions:
        return f'{name.lower()} not connected.'
    await client.close_session(name.lower())
    return f'{name.lower()} now disconnected.'
