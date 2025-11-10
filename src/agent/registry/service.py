from src.mcp.types.tools import ToolResult as MCPToolResult
from src.agent.registry.views import ToolResult
from src.mcp.client.service import Session
from functools import partial
from textwrap import dedent
from src.tool import Tool
import asyncio
import json

class Registry:
    def __init__(self,tools:list[Tool]=[]):
        self.mcp_tools:list[Tool]=[]
        self.tools=tools

    def tool_prompt(self, tool_name: str) -> str:
        tool = self.registry_tools.get(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' not found."
        return dedent(f"""
        Tool Name: {tool.name}
        Tool Description: {tool.description}
        Tool Schema: {json.dumps(tool.args_schema,indent=4)}
        """)

    @property
    def registry_tools(self):
        tools=self.tools+self.mcp_tools
        return {tool.name: tool for tool in tools}
    
    def get_tools_prompt(self) -> str:
        tools_prompt = [self.tool_prompt(tool.name) for tool in self.registry_tools.values()]
        return '\n\n'.join(tools_prompt)
    
    def add_tool(self, tool: Tool):
        self.tools.append(tool)
    
    def add_tools(self, tools: list[Tool]):
        self.tools.extend(tools)
    
    async def add_tools_from_session(self,mcp_session:Session):
        mcp_tools=await mcp_session.tools_list()
        tools=[Tool(
            name=mcp_tool.name,
            description=mcp_tool.description,
            args_schema=mcp_tool.inputSchema,
            func=partial(mcp_session.tools_call,mcp_tool.name),
        ) for mcp_tool in mcp_tools]
        self.mcp_tools.extend(tools)
    
    async def add_tools_from_sessions(self,sessions:list[Session]):
        self.mcp_tools=[]
        await asyncio.gather(*[self.add_tools_from_session(session) for session in sessions])

    def _sanitize_kwargs(self, tool: Tool, kwargs: dict) -> dict:
        # For MCP tools (dict schema, no pydantic model), keep only schema-defined keys
        if tool.model is None and isinstance(tool.args_schema, dict):
            properties = tool.args_schema.get('properties', {})
            allowed = set(properties.keys())
            return {k: v for k, v in kwargs.items() if k in allowed}
        # For internal tools (pydantic models), pass through; models allow extra fields
        return kwargs

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.registry_tools.get(tool_name)
        if tool is None:
            return ToolResult(is_success=False, error=f"Tool '{tool_name}' not found.")
        try:
            # Validate only if a pydantic model is present
            if tool.model is not None:
                tool.model.model_validate(kwargs)
            content = tool.invoke(**self._sanitize_kwargs(tool, kwargs))
            if isinstance(content, MCPToolResult):
                content = content.content
            return ToolResult(is_success=True, content=content)
        except Exception as error:
            return ToolResult(is_success=False, error=str(error))
        
    async def aexecute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.registry_tools.get(tool_name)
        if tool is None:
            return ToolResult(is_success=False, error=f"Tool '{tool_name}' not found.")
        try:
            # Validate only if a pydantic model is present
            if tool.model is not None:
                tool.model.model_validate(kwargs)
            content = await tool.ainvoke(**self._sanitize_kwargs(tool, kwargs))
            if isinstance(content, MCPToolResult):
                content = content.content
            return ToolResult(is_success=True, content=content)
        except Exception as error:
            return ToolResult(is_success=False, error=str(error))
