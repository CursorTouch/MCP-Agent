from src.mcp.types.tools import Tool as MCPTool, ToolResult as MCPToolResult
from src.mcp.client.service import MCPClient,Session
from src.agent.registry.views import ToolResult
from functools import partial
from textwrap import dedent
from src.tool import Tool
import json

class Registry:
    def __init__(self,tools:list[Tool]):
        self.mcp_tools:list[MCPTool]=[]
        self.tools=tools
        self.tools_registry=self.registry()

    def tool_prompt(self, tool_name: str) -> str:
        tool = self.tools_registry.get(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' not found."
        return dedent(f"""
        Tool Name: {tool.name}
        Tool Description: {tool.description}
        Tool Schema: {json.dumps(tool.args_schema,indent=4)}
        """)

    def registry(self):
        return {tool.name: tool for tool in self.tools}
    
    def get_tools_prompt(self) -> str:
        tools_prompt = [self.tool_prompt(tool.name) for tool in self.tools+self.mcp_tools]
        return '\n\n'.join(tools_prompt)
    
    def add_tool(self, tool: Tool):
        self.tools.append(tool)
        self.tools_registry[tool.name] = tool
    
    def add_tools(self, tools: list[Tool]):
        self.tools.extend(tools)
        self.tools_registry.update({tool.name: tool for tool in tools})
    
    async def add_tools_from_session(self,session:Session):
        mcp_tools=await session.tools_list()
        tools=[Tool(
            name=mcp_tool.name,
            description=mcp_tool.description,
            args_schema=mcp_tool.inputSchema,
            func=partial(session.tools_call,mcp_tool.name)
        ) for mcp_tool in mcp_tools]
        self.mcp_tools.extend(tools)
        self.tools_registry.update({tool.name: tool for tool in tools})
    
    async def add_tools_from_sessions(self,sessions:list[Session]):
        for tool in self.mcp_tools:
            if tool.name in self.tools_registry:
                del self.tools_registry[tool.name]
        self.mcp_tools=[]
        for session in sessions:
            await self.add_tools_from_session(session)

    def _sanitize_kwargs(self, tool: Tool, kwargs: dict) -> dict:
        # For MCP tools (dict schema, no pydantic model), keep only schema-defined keys
        if tool.model is None and isinstance(tool.args_schema, dict):
            properties = tool.args_schema.get('properties', {})
            allowed = set(properties.keys())
            return {k: v for k, v in kwargs.items() if k in allowed}
        # For internal tools (pydantic models), pass through; models allow extra fields
        return kwargs

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.tools_registry.get(tool_name)
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
        tool = self.tools_registry.get(tool_name)
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