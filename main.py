from src.llms.google import ChatGoogle
from src.llms.mistral import ChatMistral
from src.mcp.client import MCPClient
from src.agent.service import Agent
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatMistral(model='magistral-small-latest',api_key=os.getenv('MISTRAL_API_KEY'),temperature=0)
client=MCPClient.from_config_file('./config.json')
agent=Agent(mcp_client=client,llm=llm)

async def main():
    task=input('Enter a task: ')
    await agent.invoke(task=task)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())