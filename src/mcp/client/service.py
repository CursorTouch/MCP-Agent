from src.mcp.client.utils import create_transport_from_server_config
from src.mcp.types.elicitation import ElicitationFn
from src.mcp.registry.service import MCPRegistry
from src.mcp.types.sampling import SamplingFn
from src.mcp.client.session import MCPSession
from src.mcp.types.roots import ListRootsFn
from src.mcp.types.info import ClientInfo
from typing import Callable, Optional
from uuid import uuid4
from typing import Any
import json

class MCPClient:
    client_info=ClientInfo(name="MCP Client",version="0.1.0")
    def __init__(self,config:dict[str,dict[str,Any]]={},sampling_callback:Optional[SamplingFn]=None,elicitation_callback:Optional[ElicitationFn]=None,list_roots_callback:Optional[ListRootsFn]=None)->None:
        self.servers=config.get("mcpServers",{})
        self.sampling_callback=sampling_callback
        self.list_roots_callback=list_roots_callback
        self.elicitation_callback=elicitation_callback
        self.sessions:dict[str,MCPSession]={}
        self.registry=MCPRegistry()
        
    @classmethod
    def from_config(cls,config:dict[str,dict[str,Any]],sampling_callback:Optional[Callable]=None,elicitation_callback:Optional[Callable]=None,list_roots_callback:Optional[Callable]=None,logging_callback:Optional[Callable]=None)->'MCPClient':
        '''Create a client from a configuration'''
        return cls(config=config,sampling_callback=sampling_callback,elicitation_callback=elicitation_callback,list_roots_callback=list_roots_callback,logging_callback=logging_callback)
    
    @classmethod
    def from_config_file(cls,config_file_path:str)->'MCPClient':
        '''Create a client from a configuration file'''
        with open(config_file_path) as f:
            config=json.load(f)
        return cls(config=config)
    
    def get_server_names(self)->list[str]:
        '''Get the MCP server names'''
        return list(self.servers.keys())
    
    def get_servers_info(self)->list[dict[str,Any]]:
        '''Get the MCP servers information'''
        return [{
            'id':str(uuid4()),
            'name':name,
            'description':config.get("description",""),
            'status':self.is_connected(name)
        } for name,config in self.servers.items()]

    def to_config_file(self,config_file_path:str)->None:
        '''Save the MCP servers configuration to a file'''
        with open(config_file_path,"w") as f:
            json.dump(self.to_config(),f,indent=4)

    def to_config(self)->dict[str,dict[str,Any]]:
        '''Get the MCP servers configuration'''
        return {"mcpServers":self.servers}

    def add_server(self,name:str,config:dict[str,Any],auto_connect:bool=False)->None:
        '''Add a server'''
        if name in self.servers:
            raise ValueError(f"{name} already exists")
        self.servers[name]=config
        if auto_connect:
            self.create_session(name)

    def remove_server(self,name:str)->None:
        '''Remove a server'''
        if self.get_session(name):
            self.close_session(name)
        del self.servers[name]

    async def create_session(self,name:str)->MCPSession:
        '''Create a MCPSession'''
        if not self.servers:
            raise Exception("No MCP servers available")
        if name not in self.servers:
            raise ValueError(f"{name} not found")
        server_config=self.servers.get(name)
        transport=create_transport_from_server_config(server_config=server_config)
        transport.attach_callbacks({
            'sampling':self.sampling_callback,
            'elicitation':self.elicitation_callback,
            'list_roots':self.list_roots_callback,
        })
        session=MCPSession(transport=transport,client_info=self.client_info)
        await session.connect()
        await session.initialize()
        self.sessions[name]=session
        return session
    
    def is_connected(self,server_name:str)->bool:
        '''Check if a session is connected'''
        return server_name in self.sessions
    
    def get_all_sessions(self)->list[MCPSession]:
        '''Get all sessions'''
        return list(self.sessions.values())
    
    def get_session(self,name:str)->MCPSession|None:
        '''Get a session'''
        if not self.is_connected(name):
            raise ValueError(f"Session {name} not found")
        return self.sessions.get(name)
    
    async def close_session(self,name:str)->None:
        '''Close a session'''
        if not self.is_connected(name):
            raise ValueError(f"Session {name} not found")
        session=self.sessions.get(name)
        await session.shutdown()
        del self.sessions[name]

    async def create_all_sessions(self)->None:
        '''Create a session for each server'''
        if not self.servers:
            raise Exception("No MCP servers available")
        for name in self.servers:
            await self.create_session(name=name)

    async def close_all_sessions(self)->None:
        '''Close all sessions'''
        if not self.sessions:
            return None
        for name in list(self.sessions.keys()):
            await self.close_session(name=name)
    

        

