from src.inference.gemini import ChatGemini
from src.mcp.client import MCPClient
from src.agent.mcp import MCPAgent
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatGemini(model='gemini-2.5-flash-lite',api_key=os.getenv('GOOGLE_API_KEY'),temperature=0)
client=MCPClient.from_config_file('./config.json')
agent=MCPAgent(client=client,llm=llm,verbose=True,max_iteration=100)

input=input('Enter a task: ')

async def main():
    response=await agent.invoke(input=input)
    print(response)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())