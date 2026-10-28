import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

AVIATIONSTACK_API_KEY=os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient({
    "tavily": {
        "transport": "http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
    },


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

async def main():
    tools=await client.get_tools()

    search_tool=next(
        tool
        for tool in tools
        if tool.name=="tavily_search"
        
    )

    result=await search_tool.ainvoke({
        "query":"best hotel in delhi"
    })

    print(result)


asyncio.run(main())
search_tool=None
aviation_tools={}
async def initialize_mcp():
    global search_tool
    global aviation_tools
    if search_tool is not None and aviation_tools:
        return

    tools=await client.get_tools()

    for tool in tools:
        print(tool.name)

    search_tool=next(
        tool
        for tool in tools
        if tool.name=="tavily_search"  
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }

    

async def tavily_mcp_search(query:str):
        await initialize_mcp()
        result=await search_tool.ainvoke({
        "query":query
        })
        return result

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result

async def get_airports():

    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result

async def get_airlines():

    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool:
        return "Airline tool unavailable"

    result = await tool.ainvoke({})

    return result

if __name__ =="__main__":
    asyncio.run(main())

