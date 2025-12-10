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
import json

class Agent:
    def __init__(self,mcp_client:MCPClient,llm:BaseChatLLM,max_steps:int=20):
        self.current_thread:Optional[Thread]=None
        self.mcp_tools:dict[str,Tool]={}
        self.max_steps=max_steps
        self.threads:dict[str,Thread]={}
        self.mcp_client=mcp_client
        self.llm=llm

    async def llm_call(self):
        if self.current_thread.server:
            mcp_session=self.mcp_client.get_session(self.current_thread.server.lower())
            self.mcp_tools={tool.name:Tool(
                name=tool.name,
                description=tool.description,
                args_schema=tool.inputSchema,
                func=partial(mcp_session.tools_call,tool.name)
            ) for tool in await mcp_session.tools_list()}
            # Fix: Allow Stop Tool in child threads so they can finish
            tools=list(self.mcp_tools.values())+[start_tool, switch_tool, stop_tool]
        else:
            tools=[start_tool,stop_tool,switch_tool]
        system_prompt=Prompt.system(self.mcp_client,tools,self.current_thread,list(self.threads.values()))
        response=await self.llm.ainvoke(messages=[SystemMessage(content=system_prompt)]+self.current_thread.messages)
        tool=xml_preprocessor(response.content.content)
        return tool
    
    async def tool_call(self,tool_name:str,tool_args:dict[str,Any]):
        self.current_thread.messages.append(AIMessage(content=json.dumps({"tool_name":tool_name,"tool_args":tool_args})))
        match tool_name:
            case "Start Tool":
                tool_result = await start_tool.ainvoke(agent=self, **tool_args)
            case "Stop Tool":
                tool_result = await stop_tool.ainvoke(agent=self, **tool_args)
            case "Switch Tool":
                tool_result = await switch_tool.ainvoke(agent=self, **tool_args)
            case _:
                if tool_name in self.mcp_tools:
                    try:
                        tool_results=await self.mcp_tools[tool_name].ainvoke(**tool_args)
                        images,texts=[],[]
                        for tool_result in tool_results.content:
                            if isinstance(tool_result,ImageContent):
                                images.append(tool_result.data)
                            elif isinstance(tool_result,TextContent):
                                texts.append(tool_result.text)
                            else:
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
        for _ in range(self.max_steps):
            # Track which thread is active BEFORE the execution
            current_thread_id_before = self.current_thread.id
            
            tool=await self.llm_call()
            tool_name=tool.get("tool_name")
            tool_args=tool.get("tool_args")
            print(f"Tool Call: {tool_name}({', '.join([f'{key}={value}' for key,value in tool_args.items()])})")
            tool_result=await self.tool_call(tool_name=tool_name,tool_args=tool_args)
            print(f"Tool Result: {tool_result}")
            
            # Break only if we were in the main thread AND called Stop Tool
            if current_thread_id_before=="thread-main" and tool_name=="Stop Tool":
                break