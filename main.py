from src.llms.google import ChatGoogle
from src.llms.ollama import ChatOllama
from src.llms.open_router import ChatOpenRouter
from src.llms.mistral import ChatMistral
from src.mcp.client import MCPClient
from src.process.service import Process
from dotenv import load_dotenv
import os

load_dotenv()

llm=ChatMistral(model='mistral-small-latest',api_key=os.getenv('MISTRAL_API_KEY'),temperature=0.4)
# llm=ChatOllama(model='qwen3-vl:235b-cloud',temperature=0)
# llm=ChatOpenRouter(model='qwen/qwen3-coder:free',api_key=os.getenv('OPENROUTER_API_KEY'),temperature=0)
# llm=ChatGoogle(api_key=os.getenv('GOOGLE_API_KEY'),model='gemini-2.0-flash-exp',temperature=0)
mcp_client=MCPClient.from_config_file('./config.json')
process=Process(mcp_client=mcp_client,llm=llm)

async def main():
    task=input('Enter a task: ')
    result = await process.ainvoke(task=task)
    print(result)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())