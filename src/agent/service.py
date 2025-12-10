from src.messages import SystemMessage,HumanMessage,AIMessage,ImageMessage
from src.agent.tools.service import start_tool,stop_tool,switch_tool
from src.mcp.types.tools import TextContent,ImageContent
from src.agent.utils import xml_preprocessor
from src.agent.prompt.service import Prompt
from src.llms.base import BaseChatLLM
from src.mcp.client import MCPClient
from src.tool.service import Tool
from src.agent.views import Thread
from typing import Optional,Any
from functools import partial
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Agent:
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
        if self.current_thread.server:
            server_name = self.current_thread.server.lower()
            
            # Check cache first to avoid re-fetching tools every step
            if server_name in self.mcp_server_tools:
                pass
            else:
                mcp_session=self.mcp_client.get_session(server_name)
                tools_list = await mcp_session.tools_list()
                mcp_tools={tool.name:Tool(
                    name=tool.name,
                    description=tool.description,
                    args_schema=tool.inputSchema,
                    func=partial(mcp_session.tools_call,tool.name)
                ) for tool in tools_list}
                # Update cache
                self.mcp_server_tools[server_name] = mcp_tools
                
            tools=list(self.mcp_server_tools[server_name].values())+list(self.agent_tools.values())
        else:
            tools=list(self.agent_tools.values())
        system_prompt=Prompt.system(self.mcp_client,tools,self.current_thread,list(self.threads.values()))
        response=await self.llm.ainvoke(messages=[SystemMessage(content=system_prompt)]+self.current_thread.messages)
        tool=xml_preprocessor(response.content.content)
        return tool
    
    async def tool_call(self,tool_name:str,tool_args:dict[str,Any]):
        self.current_thread.messages.append(AIMessage(content=json.dumps({"tool_name":tool_name,"tool_args":tool_args})))
        match tool_name:
            case "Start Tool"|"Switch Tool"|"Stop Tool":
                tool_result = await self.agent_tools[tool_name].ainvoke(agent=self, **tool_args)
            case _:
                current_mcp_server_tools=self.mcp_server_tools.get(self.current_thread.server.lower(),{})
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
                        content="\n".join(texts)
                        if images:
                            self.current_thread.messages.append(ImageMessage(images=images,content=content))
                        else:
                            self.current_thread.messages.append(HumanMessage(content=content))
                        tool_result=content
                    except Exception as e:
                        tool_result=f"Error calling tool {tool_name}: {str(e)}"
                else:
                    tool_result=f"Tool {tool_name} not found"
                content=f"<tool_result>{tool_result}</tool_result>"
                self.current_thread.messages.append(HumanMessage(content=content))
        return tool_result

    async def invoke(self,task:str):
        messages=[HumanMessage(content=task)]
        self.current_thread=Thread(id="thread-main",task=task,status="started",messages=messages,server="",result="",error="")
        self.threads[self.current_thread.id]=self.current_thread
        
        global_steps = 0
        while global_steps < self.max_global_steps:
            global_steps += 1
            
            # Check Per-Thread Step Limit
            if self.current_thread.step_count >= self.max_thread_steps:
                logger.warning(f"Thread {self.current_thread.id} exceeded max steps ({self.max_thread_steps}). Forcing stop.")
                # Force stop the thread
                await self.tool_call("Stop Tool", {"error": "Max thread steps exceeded. Subtask failed."})
                if self.current_thread.id == "thread-main" and self.current_thread.status in ["completed", "failed"]:
                    break
                continue

            self.current_thread.step_count += 1
            
            # Track which thread is active BEFORE the execution
            current_thread_id_before = self.current_thread.id
            
            tool=await self.llm_call()
            tool_name=tool.get("tool_name")
            tool_args=tool.get("tool_args")
            logger.info(f"🛠️ Tool Call: {tool_name}({', '.join([f'{key}={value}' for key,value in tool_args.items()])})")
            tool_result=await self.tool_call(tool_name=tool_name,tool_args=tool_args)
            logger.info(f"📃 Tool Result: {tool_result}")
            
            # Break only if we were in the main thread AND called Stop Tool
            if current_thread_id_before=="thread-main" and tool_name=="Stop Tool":
                return tool_result
        
        return "Max global steps exceeded."