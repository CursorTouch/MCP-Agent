from src.llms.google import ChatGoogle
from src.llms.ollama import ChatOllama
from src.llms.open_router import ChatOpenRouter
from src.llms.mistral import ChatMistral
from src.mcp.client import MCPClient
from src.agent.service import Agent
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatMistral(model='magistral-small-latest',api_key=os.getenv('MISTRAL_API_KEY'),temperature=0)
# llm=ChatOllama(model='qwen3-vl:235b-cloud',temperature=0)
# llm=ChatOpenRouter(model='mistralai/devstral-2512:free',api_key=os.getenv('OPENROUTER_API_KEY'),temperature=0)
# llm=ChatGoogle(api_key=os.getenv('GOOGLE_API_KEY'),model='gemini-2.5-flash',temperature=0)
client=MCPClient.from_config_file('./config.json')
agent=Agent(mcp_client=client,llm=llm)

async def main():
    task=input('Enter a task: ')
    await agent.invoke(task=task)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())