from src.mcp.types.resources import ResourceResult,TextContent as ResourceTextContent,BinaryContent as ResourceBinaryContent
from src.mcp.types.tools import ToolResult,TextContent as ToolTextContent,ImageContent as ToolImageContent
from src.messages import AIMessage,HumanMessage,SystemMessage,ImageMessage
from src.agent.tools import connect_tool,disconnect_tool,done_tool
from src.agent.utils import extract_llm_response
from src.agent.prompt.service import Prompt
from src.agent.views import AgentResponse
from src.agent.registry import Registry
from src.llms.base import BaseChatLLM
from src.mcp.client import MCPClient
import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class Agent:
    def __init__(self,client:MCPClient,llm:BaseChatLLM,max_steps:int=10,max_consecutive_failures:int=3):
        self.name="MCP Agent"
        self.description="A MCP Agent that can use mutliple MCP Servers to perform tasks using their tools."
        self.registry=Registry(tools=[connect_tool,disconnect_tool,done_tool])
        self.max_consecutive_failures=max_consecutive_failures
        self.max_steps=max_steps
        self.client=client
        self.llm=llm

    async def ainvoke(self,query:str)->str:
        messages=[]
        agent_response=None
        servers_info=self.client.get_servers_info()
        try:
            messages.append(HumanMessage(content=f"<User-Query>{query}</User-Query>"))
            for steps in range(1,self.max_steps+1):
                sessions=self.client.get_all_sessions()
                await self.registry.add_tools_from_sessions(sessions=sessions)
                system_message=SystemMessage(content=Prompt.system_prompt(**{
                    'max_steps':self.max_steps,
                    'registry':self.registry,
                    'servers_info':servers_info
                }))
                for attempt in range(self.max_consecutive_failures):
                    try:
                        llm_response=await self.llm.ainvoke([system_message,*messages])
                        response=extract_llm_response(llm_response.content)
                        break
                    except Exception as e:
                        logger.error(f"Error in LLM invocation or response extraction: {e}")
                        if attempt+1<self.max_consecutive_failures-1:
                            continue
                        logger.error(f"Max consecutive failures reached. Failed to get a valid response after {self.max_consecutive_failures} attempts.")
                        agent_response=AgentResponse(is_success=False,response=f"Failed to get a valid response after {self.max_consecutive_failures} attempts.")
                        break
                
                thought=response.get('thought','')
                logger.info(f"Step {steps}")
                logger.info(f"Thought: {response.get('thought','')}")
                action_name=response.get('action_name','')
                action_input=response.get('action_input',{})
                messages.append(AIMessage(content=Prompt.action_prompt(thought=thought,action_name=action_name,action_input=action_input)))
                action_result=await self.registry.aexecute(tool_name=action_name,**(action_input|{'client':self.client}))
                if action_name.startswith("Done"):
                    answer=action_result.content
                    logger.info(f"Final Answer: {answer}\n")
                    messages.append(HumanMessage(content=Prompt.answer_prompt(thought=thought,answer=answer)))
                    await self.client.close_all_sessions()
                    agent_response=AgentResponse(is_success=True,response=answer)
                    break
                else:
                    logger.info(f"Action: {action_name}({', '.join([f'{k}={v}' for k,v in action_input.items()])})")
                    if isinstance(action_result.content,list):
                        texts,images=[],[]
                        if isinstance(action_result,ToolResult):
                            contents=action_result.content
                            for content in contents:
                                if isinstance(content,ToolTextContent):
                                    texts.append(content.text)
                                elif isinstance(content,ToolImageContent):
                                    images.append(content.data)
                                else:
                                    # TODO handle other content types
                                    logger.warning(f"Unsupported content type: {type(content)}")
                                    pass
                        elif isinstance(action_result,ResourceResult):
                            contents=action_result.contents
                            for content in contents:
                                if isinstance(content,ResourceTextContent):
                                    texts.append(content.text)
                                else:
                                    pass
                        observation="\n".join(texts)
                        if images:
                            messages.append(ImageMessage(content=Prompt.observation_prompt(steps=steps,max_steps=self.max_steps,observation=observation),images=images))
                        elif texts:
                            messages.append(HumanMessage(content=Prompt.observation_prompt(steps=steps,max_steps=self.max_steps,observation=observation)))
                    else:
                        observation=action_result.content if action_result.is_success else action_result.error  
                        messages.append(HumanMessage(content=Prompt.observation_prompt(steps=steps,max_steps=self.max_steps,observation=observation)))
                    logger.info(f"Observation: {observation}\n")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Exiting...")
            agent_response=AgentResponse(is_success=False,response="Keyboard interrupt received. Exiting...")
        except Exception as e:
            logger.error(f"Error in agent operation: {e}")
            agent_response=AgentResponse(is_success=False,response=f"Error in agent operation: {e}")
        finally:
            # Safely close all sessions before quitting just in case agent misses to disconnect
            if self.client.get_all_sessions():
                await self.client.close_all_sessions()
        return agent_response
        
