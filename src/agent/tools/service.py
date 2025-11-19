from src.mcp.types.registry import ListServersRequest,SpecificServerVersionRequest,ListServersResponse,SpecificServerVersionResponse
from src.agent.tools.views import Done,Connect,Disconnect,Resource,Registry
from src.mcp.registry.service import MCPRegistry
from src.mcp.client import MCPClient
from typing import cast, Any,Literal
from textwrap import dedent
from src.tool import Tool

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

@Tool('Registry Tool', args_schema=Registry)
async def registry_tool(name, **kwargs):
    '''Install an MCP server from the official MCP Registry'''
    client = cast(MCPClient, kwargs['client'])
    registry=cast(MCPRegistry,client.registry)
    response:ListServersResponse=await registry.list_servers(ListServersRequest(search=name))
    if not response.servers:
        return f'No MCP servers found for {name}'
    return dedent('\n'.join([f'''
        Name: {server.server.title or server.server.name}
        Version: {server.server.version}
        Description: {server.server.description}
        {f"""Packages:{"\n".join([f'''
            Identifier: {package.identifier}
            Registry Type: {package.registryType}
            Transport: {package.transport.type}
        ''' for package in server.server.packages]).strip()}""" if server.server.packages else f"""Remotes:{"\n".join([f'''
            Type: {remote.type}
            URL: {remote.url}
        ''' for remote in server.server.remotes]).strip()}""" if server.server.remotes else ''}
    ''' for server in response.servers])).strip()
