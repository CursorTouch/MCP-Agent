from jinja2 import FileSystemLoader,Environment
from src.mcp.client import MCPClient
from src.agent.views import Thread
from src.tool.service import Tool
from importlib import resources
from pathlib import Path

class Prompt:
    env=Environment(loader=FileSystemLoader(Path(resources.files('src.agent').joinpath('prompt')).as_posix()))

    @staticmethod
    def system(mcp_client:MCPClient,tools:list[Tool],current_thread:Thread,threads:list[Thread]):
        template=Prompt.env.get_template("system.md")
        mcp_servers=mcp_client.get_servers_info()
        return template.render(mcp_servers=mcp_servers,tools=tools,current_thread=current_thread,threads=threads)