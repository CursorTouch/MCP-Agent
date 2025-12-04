from src.llms.google import ChatGoogle
from src.mcp.client import MCPClient
from src.agent.service import Agent
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatGoogle(model='gemini-2.5-flash-lite',api_key=os.getenv('GOOGLE_API_KEY'),temperature=0)
client=MCPClient.from_config_file('./config.json')
agent=Agent(mcp_client=client,llm=llm)

async def main():
    task=input('Enter a task: ')
    await agent.invoke(task=task)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())