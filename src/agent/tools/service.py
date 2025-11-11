from src.agent.tools.views import Done,Connect,Disconnect,Resource
from src.mcp.client import MCPClient
from src.tool import Tool
from typing import cast

@Tool('Done Tool',args_schema=Done)
async def done_tool(answer:str,**kwargs):
    '''To indicate that the task is completed'''
    return answer

@Tool('Resource Tool',args_schema=Resource)
async def resource_tool(name:str,uri:str,**kwargs):
    '''Access a resource from a specific MCP server via its URI'''
    client=cast(MCPClient,kwargs['client'])
    if name.lower() not in client.sessions:
        return f'{name.lower()} not connected.'
    session=client.sessions[name.lower()]
    resource=await session.resources_read(uri=uri)
    return resource

@Tool('Connect Tool',args_schema=Connect)
async def connect_tool(name:str,**kwargs):
    '''Connect to a specific MCP server'''
    client=cast(MCPClient,kwargs['client'])
    if name.lower() in client.sessions:
        return f'Server {name.lower()} already connected.'
    session=await client.create_session(name.lower())   
    client.sessions[name.lower()]=session
    return f'{name.lower()} now connected.'

@Tool('Disconnect Tool',args_schema=Disconnect)
async def disconnect_tool(name:str,**kwargs):
    '''Disconnect from a specific MCP server'''
    client=cast(MCPClient,kwargs['client'])
    if name.lower() not in client.sessions:
        return f'{name.lower()} not connected.'
    await client.close_session(name.lower())
    return f'{name.lower()} now disconnected.'
