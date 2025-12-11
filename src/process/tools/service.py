from src.process.tools.views import Start,Switch,Stop
from src.tool.service import Tool
from src.process.views import Thread
from src.messages import HumanMessage
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.agent.service import Agent

@Tool(name="Start Tool",args_schema=Start)
async def start_tool(agent:Any, subtask:str, server_name:str, **kwargs):
    '''Start a new thread and become the active thread to solve a subtask'''
    task = subtask
    messages = [HumanMessage(content=task)]
    # Capture parent thread to append result to IT, not the child
    parent_thread = agent.current_thread
    try:
        await agent.mcp_client.create_session(server_name.lower())
        
        # Create the new thread
        thread = Thread(task=task, mcp_server=server_name, status="started", messages=messages, success="", error="", parent_id=agent.current_thread.id)
        agent.threads[thread.id] = thread
        
        # Update Parent status
        parent_thread.status = "progress"
        
        # Switch context to Child
        agent.current_thread = thread
        
        tool_result = f"Started Thread ID: {thread.id}\nSubtask: {task}\nConnected Server: {server_name} Server"
    except Exception as e:
        tool_result = f"Error starting thread: {str(e)}"
    
    # Append result to PARENT (the one who called the tool)
    content = f"<tool_result>{tool_result}</tool_result>"
    parent_thread.messages.append(HumanMessage(content=content))
    return tool_result

@Tool(name="Switch Tool",args_schema=Switch)
async def switch_tool(agent:Any, id:str, **kwargs):
    '''Switch to another thread from the current thread'''
    try:
        previous_thread = agent.current_thread
        next_thread = agent.threads.get(id)
        
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
                    await agent.mcp_client.close_session(previous_server)
                    if previous_server in agent.mcp_server_tools:
                        del agent.mcp_server_tools[previous_server]
                    connection_info += f"\nDisconnected from: {previous_server} Server"
                    
                    # Connect next
                    await agent.mcp_client.create_session(next_server)
                    connection_info += f"\nConnected to: {next_server} Server"
                else:
                    connection_info += f"\nReusing active connection to: {next_server} Server"
            
            # Handle edge cases (like switching from a Thread with NO server to one WITH server)
            elif next_server and not previous_server:
                 await agent.mcp_client.create_session(next_server)
                 connection_info += f"\nConnected to: {next_server} Server"
                 
            # Handle switching FROM a server TO a thread with NO server (e.g. back to main)
            elif previous_server and not next_server:
                 await agent.mcp_client.close_session(previous_server)
                 if previous_server in agent.mcp_server_tools:
                     del agent.mcp_server_tools[previous_server]
                 connection_info += f"\nDisconnected from: {previous_server} Server"

            agent.current_thread = next_thread
            tool_result = f"Switched to Thread ID: {agent.current_thread.id} from Thread ID: {previous_thread.id}{connection_info}"
        else:
            tool_result = f"Error: Thread ID {id} not found"
    except Exception as e:
        tool_result = f"Error switching thread: {str(e)}"
    
    content = f"<tool_result>{tool_result}</tool_result>"
    agent.current_thread.messages.append(HumanMessage(content=content))
    return tool_result

@Tool(name="Stop Tool",args_schema=Stop)
async def stop_tool(agent:Any, id:str|None=None, success:str="", error:str="", **kwargs):
    '''Stop a specific thread and switch to the previous thread'''
    try:
        target_thread = agent.threads.get(id) if id else agent.current_thread
        
        target_thread.status = "completed" if success else "failed"
        target_thread.success = success
        target_thread.error = error
        
        if target_thread.mcp_server:
            server_name = target_thread.mcp_server.lower()
            await agent.mcp_client.close_session(server_name)
            # Invalidate cache because the session object in the cached tools is now closed
            if server_name in agent.mcp_server_tools:
                del agent.mcp_server_tools[server_name]
            
        tool_result = success or error or "Task Stopped"
        stop_msg = f"Stopped Thread ID: {target_thread.id}\nResult: {tool_result}"
        if target_thread.mcp_server:
            stop_msg += f"\nDisconnected from Server: {target_thread.mcp_server} Server"

        if target_thread.parent_id and target_thread.parent_id in agent.threads:
            parent_thread = agent.threads[target_thread.parent_id]
            agent.current_thread = parent_thread
            agent.current_thread.status = "started"
            stop_msg += f"\nAuto-switched back to Parent Thread ID: {parent_thread.id}"
            
            content = f"<tool_result>{stop_msg}</tool_result>"
            agent.current_thread.messages.append(HumanMessage(content=content))
        else:
            content = f"<tool_result>{stop_msg}</tool_result>"
            target_thread.messages.append(HumanMessage(content=content))
            
    except Exception as e:
        tool_result = f"Error stopping thread: {str(e)}"
        content = f"<tool_result>{tool_result}</tool_result>"
        agent.current_thread.messages.append(HumanMessage(content=content))
        
    return tool_result