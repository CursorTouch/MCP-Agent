from src.agent.mcp.tools.views import Done,Connect,Disconnect
from src.mcp.client import MCPClient
from src.tool import Tool

@Tool('Done Tool',params=Done)
async def done_tool(answer:str,client:MCPClient=None):
    '''To indicate that the task is completed'''
    return answer

@Tool('Connect Tool',params=Connect)
async def connect_tool(server_name:str,client:MCPClient=None):
    '''Connect to a specific MCP server'''
    if server_name in client.sessions:
        return f'Server {server_name} already connected.'
    session=await client.create_session(server_name.lower())
    client.sessions[server_name.lower()]=session
    return f'Server {server_name.lower()} now connected.'

@Tool('Disconnect Tool',params=Disconnect)
async def disconnect_tool(server_name:str,client:MCPClient=None):
    '''Disconnect from a specific MCP server'''
    if server_name.lower() not in client.sessions:
        return f'Server {server_name} not connected.'
    await client.close_session(server_name.lower())
    return f'Server {server_name} now disconnected.'