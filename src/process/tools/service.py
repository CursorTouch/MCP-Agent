from src.process.tools.views import Start,Switch,Stop
from src.messages import HumanMessage,AIMessage
from src.tool.service import Tool
from src.process.views import Thread
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
    # Capture parent thread to append result to IT, not the child
    parent_thread = process.current_thread
    try:
        await process.mcp_client.create_session(server_name.lower())
        logger.debug(f"[MCP] Created session for {server_name}")
        
        messages = [HumanMessage(content=task)]
        # Create the new child thread
        child_thread = Thread(task=task, mcp_server=server_name, status="started", messages=messages, success="", error="", parent_id=process.current_thread.id)
        process.threads[child_thread.id] = child_thread
        
        # Update Parent status
        parent_thread.status = "idle"
        logger.debug(f"[Thread] Created child thread {child_thread.id} from parent thread {parent_thread.id}")
        
        # Switch context to Child
        process.current_thread = child_thread
        
        tool_result = f"Started child thread ID: {child_thread.id}\nAssigned Subtask: {task}\nConnected to: {server_name} Server"
    except Exception as e:
        tool_result = f"Error starting child thread: {str(e)}"
        logger.debug(f"[Thread] Error starting child thread: {str(e)}")
    
    # Append result to PARENT (the one who called the tool)
    content = f"<tool_result>{tool_result}</tool_result>"
    parent_thread.messages.append(AIMessage(content=content))
    return tool_result

@Tool(name="Switch Tool",args_schema=Switch)
async def switch_tool(process:'Process', id:str, **kwargs):
    '''Switch to another thread from the current thread'''
    try:
        previous_thread = process.current_thread
        
        if next_thread:=process.threads.get(id):
            # MCP Session Management Logic
            previous_thread_server = previous_thread.mcp_server.lower() if previous_thread.mcp_server else None
            next_thread_server = next_thread.mcp_server.lower() if next_thread.mcp_server else None
            
            connection_info = ""
            
            # both threads have mcp server
            if previous_thread_server and next_thread_server:
                # If servers are different, switch sessions
                if previous_thread_server != next_thread_server:
                    # Disconnect previous
                    await process.mcp_client.close_session(previous_thread_server)
                    if previous_thread_server in process.mcp_server_tools:
                        del process.mcp_server_tools[previous_thread_server]
                    connection_info += f"\nDisconnected from: {previous_thread_server} Server"
                    
                    # Connect next
                    await process.mcp_client.create_session(next_thread_server)
                    connection_info += f"\nConnected to: {next_thread_server} Server"
                else:
                    connection_info += f"\nReusing active connection to: {next_thread_server} Server"
            
            # Following scenerio occurs when switching to/from main thread
            
            # next thread has mcp server and previous thread doesn't
            elif next_thread_server and not previous_thread_server:
                 await process.mcp_client.create_session(next_thread_server)
                 connection_info += f"\nConnected to: {next_thread_server} Server"
                 
            # previous thread has mcp server and next thread doesn't
            elif previous_thread_server and not next_thread_server:
                 await process.mcp_client.close_session(previous_thread_server)
                 if previous_thread_server in process.mcp_server_tools:
                     del process.mcp_server_tools[previous_thread_server]
                 connection_info += f"\nDisconnected from: {previous_thread_server} Server"

            process.current_thread = next_thread
            tool_result = f"Switched to Thread ID: {process.current_thread.id} from Thread ID: {previous_thread.id}\n{connection_info}"
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
        
        tool_result = success or error or "Task Stopped"
        stop_msg = f"Stopped Thread ID: {target_thread.id}\nStatus: {target_thread.status}\nResult: {tool_result}"

        # Close MCP session if it exists (not needed for main thread)
        if target_thread.mcp_server:
            server_name = target_thread.mcp_server.lower()
            if process.mcp_client.is_connected(server_name):
                await process.mcp_client.close_session(server_name)
                # Remove tools from cache when the session is closed
                if server_name in process.mcp_server_tools:
                    del process.mcp_server_tools[server_name]
                stop_msg += f"\nDisconnected from Server: {target_thread.mcp_server} Server"
            else:
                stop_msg += f"\n{server_name} Server already closed"
            
        # Switch to parent thread if it exists (not needed for main thread)
        if target_thread.parent_id and (target_thread.parent_id in process.threads):
            parent_thread = process.threads[target_thread.parent_id]

            # Switch to parent thread
            process.current_thread = parent_thread
            process.current_thread.status = "started"

            stop_msg += f"\nAuto-switched back to Parent Thread ID: {parent_thread.id}"
            logger.debug(f"[Thread] Auto-switched back to Parent Thread ID: {parent_thread.id}")
            


            # Append result to PARENT so it "sees" what the child did
            content = "<tool_result>{tool_result}</tool_result>"
            process.current_thread.messages.append(HumanMessage(content=content.format(tool_result=stop_msg)))
            target_thread.messages.append(HumanMessage(content=content.format(tool_result=tool_result)))
        else:
            # If no parent (Main Thread), just append to itself
            content = f"<tool_result>{stop_msg}</tool_result>"
            target_thread.messages.append(HumanMessage(content=content))
        
        logger.debug(f"[Thread] Stopped Thread ID: {target_thread.id}")
            
    except Exception as e:
        tool_result = f"Error stopping thread: {str(e)}"
        logger.debug(f"[Thread] Error stopping thread: {str(e)}")
        content = f"<tool_result>{tool_result}</tool_result>"
        process.current_thread.messages.append(HumanMessage(content=content))

    return tool_result