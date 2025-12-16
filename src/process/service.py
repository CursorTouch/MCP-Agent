from src.messages import SystemMessage,HumanMessage,AIMessage,ImageMessage
from src.process.tools.service import start_tool,stop_tool,switch_tool
from src.mcp.types.content import TextContent,ImageContent
from src.mcp.types.tools import CallToolRequestParams
from src.process.utils import xml_preprocessor
from src.process.prompt.service import Prompt
from src.llms.base import BaseChatLLM
from src.mcp.client import MCPClient
from src.tool.service import Tool
from src.process.views import Thread
from typing import Optional,Any
from functools import partial
from textwrap import shorten
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Process:
    def __init__(self,mcp_client:MCPClient,llm:BaseChatLLM,max_thread_steps:int=20,max_global_steps:int=100):
        self.current_thread:Optional[Thread]=None
        self.max_thread_steps=max_thread_steps
        self.max_global_steps=max_global_steps
        self.threads:dict[str,Thread]={}
        self.mcp_client=mcp_client
        self.llm=llm
        self.agent_tools:dict[str,Tool]={"Start Tool":start_tool,"Stop Tool":stop_tool,"Switch Tool":switch_tool}
        self.mcp_server_tools:dict[str,dict[str,Tool]]={}

    async def llm_call(self):
        if self.current_thread.mcp_server:
            server_name = self.current_thread.mcp_server.lower()
            
            # Check cache first to avoid re-fetching tools every step
            if server_name in self.mcp_server_tools:
                pass
            else:
                mcp_session = self.mcp_client.get_session(server_name)
                if mcp_session is None:
                    # Session might be closed (e.g. by a child thread sharing same server name). Reconnect.
                    logger.debug(f"Session {server_name} not found. Reconnecting for thread {self.current_thread.id}...")
                    await self.mcp_client.create_session(server_name)
                    mcp_session = self.mcp_client.get_session(server_name)

                tools_list = await mcp_session.tools_list()
                tools=tools_list.tools
                mcp_tools={tool.name:Tool(
                    name=tool.name,
                    description=tool.description,
                    args_schema=tool.inputSchema,
                    func=partial(lambda session,tool,**kwargs: session.tools_call(CallToolRequestParams(name=tool.name,arguments=kwargs)), mcp_session, tool)
                ) for tool in tools}
                # Update cache
                self.mcp_server_tools[server_name] = mcp_tools
                
            tools=list(self.mcp_server_tools[server_name].values())+list(self.agent_tools.values())
        else:
            tools=list(self.agent_tools.values())
        system_prompt=Prompt.system(mcp_client=self.mcp_client,tools=tools,current_thread=self.current_thread,threads=list(self.threads.values()))
        response=await self.llm.ainvoke(messages=[SystemMessage(content=system_prompt)]+self.current_thread.messages)
        decision=xml_preprocessor(response.content.content)
        return decision
    
    async def tool_call(self,tool_name:str,tool_args:dict[str,Any]):
        tool_call_content=f"<tool_name>{tool_name}</tool_name><tool_args>{' '.join([f'<{key}>{value}</{key}>' for key,value in tool_args.items()])}</tool_args>"
        self.current_thread.messages.append(AIMessage(content=tool_call_content))
        match tool_name:
            case "Start Tool"|"Switch Tool"|"Stop Tool":
                tool=self.agent_tools[tool_name]
                logger.debug(f"[Tool Call] {tool_name}({', '.join([f'{key}={value}' for key,value in tool_args.items()])})")
                tool_result = await tool.ainvoke(process=self, **tool_args)
                logger.debug(f"[Tool Result] {tool_result}")
                return tool_result
            case _:
                current_mcp_server_tools=self.mcp_server_tools.get(self.current_thread.mcp_server.lower(),{})
                if tool_name in current_mcp_server_tools:
                    try:
                        tool=current_mcp_server_tools[tool_name]
                        tool_results=await tool.ainvoke(**tool_args)
                        images,texts=[],[]
                        for tool_result in tool_results.content:
                            if isinstance(tool_result,ImageContent):
                                images.append(tool_result.data)
                            elif isinstance(tool_result,TextContent):
                                texts.append(tool_result.text)
                            else:
                                # TODO: Handle other types of tool results
                                pass
                        tool_result="\n".join(texts)
                        content=f"<tool_result>{tool_result}</tool_result>"
                        if images:
                            self.current_thread.messages.append(ImageMessage(images=images,content=content))
                        else:
                            self.current_thread.messages.append(HumanMessage(content=content))
                        return tool_result
                        
                    except Exception as e:
                        tool_result=f"Error calling tool {tool_name}: {str(e)}"
                        logger.debug(f"[Tool Result] {tool_result}")

                else:
                    tool_result=f"Tool {tool_name} not found"
                    logger.debug(f"[Tool Result] {tool_result}")

                content=f"<tool_result>{tool_result}</tool_result>"
                self.current_thread.messages.append(HumanMessage(content=content))
                return tool_result

    async def ainvoke(self,task:str):
        try:
            messages=[HumanMessage(content=task)]
            self.current_thread=Thread(id="thread-main",task=task,status="started",messages=messages, mcp_server="", success="",error="")
            self.threads[self.current_thread.id]=self.current_thread

            logger.info(f"▶️  Starting Thread:")
            logger.info(f"🧵 Thread ID: {self.current_thread.id}")
            logger.info(f"🎯 Main Task: {self.current_thread.task}")
            print()
            
            global_steps = 0
            while global_steps < self.max_global_steps:
                global_steps += 1
                
                # Check Per-Thread Step Limit
                if self.current_thread.step_count >= self.max_thread_steps:
                    logger.warning(f"Thread {self.current_thread.id} exceeded max steps ({self.max_thread_steps}). Forcing stop.")
                    # Force stop the current thread
                    await self.tool_call("Stop Tool", {"id": self.current_thread.id, "error": f"Exceeded max steps. {'Subtask' if self.current_thread.id != 'thread-main' else 'Main Task'} failed forced to stop."})
                    # Check if the current thread is the main thread and if it is completed or failed
                    if self.current_thread.id == "thread-main" and self.current_thread.status in ["completed", "failed"]:
                        break
                    else:
                        # After switching to the parent thread 
                        # If the current thread is not the main thread, continue to the next iteration
                        continue

                self.current_thread.step_count += 1
                
                # Track which thread is active BEFORE the execution
                current_thread_id_before = self.current_thread.id
                current_thread_mcp_server_before = self.current_thread.mcp_server
                
                try:
                    decision=await self.llm_call()
                    tool_name=decision.get("tool_name")
                    tool_args=decision.get("tool_args")

                    tool_result=await self.tool_call(tool_name=tool_name,tool_args=tool_args)

                    match tool_name:
                        case "Start Tool":
                            logger.info(f"▶️  Starting Thread:")
                            logger.info(f"🧵 Thread ID: {self.current_thread.id}")
                            logger.info(f"📌 Subtask: {self.current_thread.task}")
                            logger.info(f"🔌 Connected to: {self.current_thread.mcp_server}")
                            if self.current_thread.parent_id:
                                logger.info(f"🧶 Parent Thread ID: {self.current_thread.parent_id}")

                        case "Switch Tool":
                            logger.info(f"🔄  Switching Thread:")
                            logger.info(f"From 🧵 Thread ID: {current_thread_id_before}")
                            if current_thread_mcp_server_before!=self.current_thread.mcp_server:
                                logger.info(f"🔌 Disconnecting from: {current_thread_mcp_server_before}")
                            logger.info(f"To 🧵 Thread ID: {self.current_thread.id}")
                            if self.current_thread.mcp_server!=current_thread_mcp_server_before:
                                logger.info(f"🔌 Connecting to: {self.current_thread.mcp_server}")

                        case "Stop Tool":
                            logger.info(f"⏹️  Stopping Thread:")
                            logger.info(f"🧵 Thread ID: {current_thread_id_before}")
                            if tool_args.get("error"):
                                logger.info(f"❌ Error: {tool_args.get('error')}")
                            else:
                                logger.info(f"✅ Success: {tool_args.get('success', 'Task Completed')}")
                            if current_thread_mcp_server_before:
                                logger.info(f"🔌 Disconnected from: {current_thread_mcp_server_before}")

                        case _:
                            thought=decision.get("thought")
                            logger.info(f"🧠 Thought: {thought}")
                            logger.info(f"🔧 Tool Call: {tool_name}({', '.join([f'{key}={value}' for key,value in tool_args.items()])})")
                            logger.info(f"📄 Tool Result: {shorten(tool_result, width=500, placeholder='...')}")

                    print()
                    # Break only if we were in the main thread AND called Stop Tool
                    if current_thread_id_before=="thread-main" and tool_name=="Stop Tool":
                        return tool_result

                except Exception as e:
                    logger.error(f"Thread ID {self.current_thread.id} Crashed: {e}", exc_info=True)
                    error_msg = f"Thread ID {self.current_thread.id} Execution Failed: {str(e)}"
                    # Force stop the crashing thread, allowing parent to recover
                    stop_result = await self.tool_call("Stop Tool", {"error": error_msg})
                    
                    # If Main Thread crashed, we can't recover
                    if current_thread_id_before == "thread-main":
                        logger.warn("⚠️ Main Thread Crashed. Closing all MCP sessions...")
                        await self.mcp_client.close_all_sessions()
                        return f"Process Crashed: {stop_result}"
            
            return "Max global steps exceeded."
        except (KeyboardInterrupt,asyncio.CancelledError):
            logger.warn("⚠️ KeyboardInterrupt. Closing all MCP sessions...")
            await self.mcp_client.close_all_sessions()
            return "Process Interrupted."
