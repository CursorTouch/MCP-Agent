from src.agent.tools.views import Start,Switch,Stop
from src.tool.service import Tool
from src.agent.views import Thread
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
        thread = Thread(task=task, server=server_name, status="started", messages=messages, result="", error="", parent_id=agent.current_thread.id)
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
            agent.current_thread = next_thread
            tool_result = f"Switched to Thread ID: {agent.current_thread.id} from Thread ID: {previous_thread.id}"
        else:
            tool_result = f"Error: Thread ID {id} not found"
    except Exception as e:
        tool_result = f"Error switching thread: {str(e)}"
    
    content = f"<tool_result>{tool_result}</tool_result>"
    agent.current_thread.messages.append(HumanMessage(content=content))
    return tool_result

@Tool(name="Stop Tool",args_schema=Stop)
async def stop_tool(agent:Any, id:str|None=None, result:str="", error:str="", **kwargs):
    '''Stop a specific thread and switch to the previous thread'''
    try:
        target_thread = agent.threads.get(id) if id else agent.current_thread
        
        target_thread.status = "completed" if result else "failed"
        target_thread.result = result
        target_thread.error = error
        
        if target_thread.server:
            await agent.mcp_client.close_session(target_thread.server.lower())
            
        tool_result = result or error or "Task Stopped"
        stop_msg = f"Stopped Thread ID: {target_thread.id}\nResult: {tool_result}"
        if target_thread.server:
            stop_msg += f"\nDisconnected from Server: {target_thread.server} Server"

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