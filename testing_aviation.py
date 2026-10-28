import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

AVIATIONSTACK_API_KEY=os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient(
    {
        "aviationstack": {
            "transport": "stdio",
            "command": r"C:\Users\ADITYA KUMAR ROY\production-rag-app\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATIONSTACK_API_KEY": AVIATIONSTACK_API_KEY
            }
        }

    }
)

import asyncio

async def main():

    tools=await client.get_tools()

    for tool in tools:
        print(tool.name)

asyncio.run(main())
