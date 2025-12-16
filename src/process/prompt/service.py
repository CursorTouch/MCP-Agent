from jinja2 import FileSystemLoader,Environment
from src.mcp.client import MCPClient
from src.process.views import Thread
from src.tool.service import Tool
from importlib import resources
from pathlib import Path

class Prompt:
    env=Environment(loader=FileSystemLoader(Path(resources.files('src.process').joinpath('prompt')).as_posix()))
    @staticmethod
    def system(mcp_client:MCPClient,tools:list[Tool],current_thread:Thread,threads:list[Thread]):
        template=Prompt.env.get_template("system.md")
        mcp_servers=mcp_client.get_servers_info()
        
        # HIERARCHICAL VISIBILITY implementation:
        # Only show the Current Thread and its immediate Children.
        
        # This hides the Parent thread (and its global goal) from the Child, preventing context leakage.
        visible_threads = [current_thread] + [t for t in threads if t.parent_id == current_thread.id]
        
        return template.render(mcp_servers=mcp_servers,tools=tools,current_thread=current_thread,threads=visible_threads)