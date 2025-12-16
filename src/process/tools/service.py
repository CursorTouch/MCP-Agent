from src.process.tools.views import Start,Switch,Stop
from src.tool.service import Tool
from src.process.views import Thread
from src.messages import HumanMessage
from typing import TYPE_CHECKING, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if TYPE_CHECKING:
    from src.process.service import Process

@Tool(name="Start Tool",args_schema=Start)
async def start_tool(process:'Process', subtask:str, server_name:str, **kwargs):
    '''Start a new thread and become the active thread to solve a subtask'''
    task = subtask
    messages = [HumanMessage(content=task)]
    # Capture parent thread to append result to IT, not the child
    parent_thread = process.current_thread
    try:
        await process.mcp_client.create_session(server_name.lower())
        logger.debug(f"[MCP] Created session for {server_name}")
        
        # Create the new thread
        thread = Thread(task=task, mcp_server=server_name, status="started", messages=messages, success="", error="", parent_id=process.current_thread.id)
        process.threads[thread.id] = thread
        
        # Update Parent status
        parent_thread.status = "progress"
        logger.debug(f"[Thread] Created thread {thread.id}")
        
        # Switch context to Child
        process.current_thread = thread
        
        tool_result = f"Started Thread ID: {thread.id}\nParent Thread ID: {parent_thread.id}\nSubtask: {task}\nConnected Server: {server_name} Server"
    except Exception as e:
        tool_result = f"Error starting thread: {str(e)}"
        logger.debug(f"[Thread] Error starting thread: {str(e)}")
    
    # Append result to PARENT (the one who called the tool)
    content = f"<tool_result>{tool_result}</tool_result>"
    parent_thread.messages.append(HumanMessage(content=content))
    return tool_result

@Tool(name="Switch Tool",args_schema=Switch)
async def switch_tool(process:'Process', id:str, **kwargs):
    '''Switch to another thread from the current thread'''
    try:
        previous_thread = process.current_thread
        next_thread = process.threads.get(id)
        
        if next_thread:
            # MCP Session Management Logic
            previous_server = previous_thread.mcp_server.lower() if previous_thread.mcp_server else None
            next_server = next_thread.mcp_server.lower() if next_thread.mcp_server else None
            
            connection_info = ""
            
            # valid both servers
            if previous_server and next_server:
                # If servers are different, we need to switch sessions
                if previous_server != next_server:
                    # Disconnect previous
                    await process.mcp_client.close_session(previous_server)
                    if previous_server in process.mcp_server_tools:
                        del process.mcp_server_tools[previous_server]
                    connection_info += f"\nDisconnected from: {previous_server} Server"
                    
                    # Connect next
                    await process.mcp_client.create_session(next_server)
                    connection_info += f"\nConnected to: {next_server} Server"
                else:
                    connection_info += f"\nReusing active connection to: {next_server} Server"
            
            # Handle edge cases (like switching from a Thread with NO server to one WITH server)
            elif next_server and not previous_server:
                 await process.mcp_client.create_session(next_server)
                 connection_info += f"\nConnected to: {next_server} Server"
                 
            # Handle switching FROM a server TO a thread with NO server (e.g. back to main)
            elif previous_server and not next_server:
                 await process.mcp_client.close_session(previous_server)
                 if previous_server in process.mcp_server_tools:
                     del process.mcp_server_tools[previous_server]
                 connection_info += f"\nDisconnected from: {previous_server} Server"

            process.current_thread = next_thread
            tool_result = f"Switched to Thread ID: {process.current_thread.id} from Thread ID: {previous_thread.id}{connection_info}"
            logger.debug(f"[Thread] Switched to Thread ID: {process.current_thread.id} from Thread ID: {previous_thread.id}{connection_info}")
        else:
            tool_result = f"Error: Thread ID {id} not found"
            logger.debug(f"[Thread] Error: Thread ID {id} not found")
    except Exception as e:
        tool_result = f"Error switching thread: {str(e)}"
        logger.debug(f"[Thread] Error switching thread: {str(e)}")
    
    content = f"<tool_result>{tool_result}</tool_result>"
    process.current_thread.messages.append(HumanMessage(content=content))
    return tool_result

@Tool(name="Stop Tool",args_schema=Stop)
async def stop_tool(process:'Process', id:str|None=None, success:str="", error:str="", **kwargs):
    '''Stop a specific thread and switch to the previous thread'''
    try:
        target_thread = process.threads.get(id) if id else process.current_thread
        
        target_thread.status = "completed" if success else "failed"
        target_thread.success = success
        target_thread.error = error
        
        if target_thread.mcp_server:
            server_name = target_thread.mcp_server.lower()
            if process.mcp_client.is_connected(server_name):
                await process.mcp_client.close_session(server_name)
                # Invalidate cache because the session object in the cached tools is now closed
                if server_name in process.mcp_server_tools:
                    del process.mcp_server_tools[server_name]
                logger.debug(f"[MCP] Closed session for {server_name}")
            else:
                 logger.debug(f"[MCP] Session {server_name} already closed")
            
        tool_result = success or error or "Task Stopped"
        stop_msg = f"Stopped Thread ID: {target_thread.id}\nResult: {tool_result}"
        if target_thread.mcp_server:
            stop_msg += f"\nDisconnected from Server: {target_thread.mcp_server} Server"

        if target_thread.parent_id and target_thread.parent_id in process.threads:
            parent_thread = process.threads[target_thread.parent_id]
            process.current_thread = parent_thread
            process.current_thread.status = "started"
            stop_msg += f"\nAuto-switched back to Parent Thread ID: {parent_thread.id}"
            
        content = f"<tool_result>{stop_msg}</tool_result>"
        target_thread.messages.append(HumanMessage(content=content))
        logger.debug(f"[Thread] Stopped Thread ID: {target_thread.id}")
            
    except Exception as e:
        tool_result = f"Error stopping thread: {str(e)}"
        logger.debug(f"[Thread] Error stopping thread: {str(e)}")
        content = f"<tool_result>{tool_result}</tool_result>"
        process.current_thread.messages.append(HumanMessage(content=content))
        
    return tool_result